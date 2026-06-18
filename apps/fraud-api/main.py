import os
import json
import time
import uuid
import urllib.request
from collections import deque
from typing import Literal

from fastapi import FastAPI, Header, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest
from pydantic import BaseModel, Field


APP_NAME = "FinGuard Lite Fraud API"


def load_vault_overrides() -> dict[str, str]:
    vault_addr = os.getenv("VAULT_ADDR", "").rstrip("/")
    vault_token = os.getenv("VAULT_TOKEN", "")
    secret_path = os.getenv("VAULT_SECRET_PATH", "").strip("/")
    if not vault_addr or not vault_token or not secret_path:
        return {}

    request = urllib.request.Request(
        f"{vault_addr}/v1/{secret_path}",
        headers={"X-Vault-Token": vault_token},
    )
    try:
        with urllib.request.urlopen(request, timeout=2) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception as error:
        print(
            json.dumps({"event": "vault_secret_unavailable", "error": str(error)}),
            flush=True,
        )
        return {}

    secret = payload.get("data", {}).get("data", {})
    return {key: str(value) for key, value in secret.items()}


VAULT_OVERRIDES = load_vault_overrides()
REVIEW_THRESHOLD = int(VAULT_OVERRIDES.get("FRAUD_REVIEW_THRESHOLD", os.getenv("FRAUD_REVIEW_THRESHOLD", "45")))
BLOCK_THRESHOLD = int(VAULT_OVERRIDES.get("FRAUD_BLOCK_THRESHOLD", os.getenv("FRAUD_BLOCK_THRESHOLD", "75")))
API_TOKEN = VAULT_OVERRIDES.get("FINGUARD_API_TOKEN", os.getenv("FINGUARD_API_TOKEN", ""))
RECENT_LIMIT = int(os.getenv("RECENT_TRANSACTION_LIMIT", "25"))

RECENT_TRANSACTIONS: deque[dict] = deque(maxlen=RECENT_LIMIT)

HTTP_REQUESTS = Counter(
    "finguard_http_requests_total",
    "HTTP requests received by FinGuard API.",
    ["method", "path", "status"],
)
HTTP_LATENCY = Histogram(
    "finguard_http_request_duration_seconds",
    "Request latency in seconds.",
    ["path"],
)
TRANSACTIONS = Counter(
    "finguard_transactions_total",
    "Transactions scored by decision.",
    ["decision"],
)
SECURITY_EVENTS = Counter(
    "finguard_security_events_total",
    "Rejected or suspicious API access events.",
    ["event_type"],
)
LATEST_RISK_SCORE = Gauge(
    "finguard_latest_risk_score",
    "Most recent transaction risk score.",
)

app = FastAPI(title=APP_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Transaction(BaseModel):
    transactionId: str = Field(..., min_length=3, examples=["txn-1001"])
    amount: float = Field(..., ge=0, examples=[95000])
    currency: str = Field(default="INR", min_length=3, max_length=3)
    country: str = Field(default="IN", min_length=2, max_length=2)
    deviceId: str = Field(..., min_length=2, examples=["device-22"])
    customerId: str = Field(..., min_length=2, examples=["cust-10"])
    failedLogins: int = Field(default=0, ge=0, le=50)
    velocity: int = Field(default=0, ge=0, le=100)
    networkStatus: Literal["OK", "DEGRADED", "DOWN"] = "OK"


class ScoreResponse(BaseModel):
    transactionId: str
    riskScore: int
    decision: Literal["ALLOW", "REVIEW", "BLOCK"]
    reasons: list[str]
    traceId: str


def require_token(x_api_token: str | None) -> None:
    if not API_TOKEN:
        return
    if x_api_token != API_TOKEN:
        SECURITY_EVENTS.labels(event_type="invalid_api_token").inc()
        raise HTTPException(status_code=401, detail="Invalid API token")


def score_transaction(transaction: Transaction) -> tuple[int, list[str]]:
    score = 5
    reasons: list[str] = []

    if transaction.amount >= 100000:
        score += 35
        reasons.append("high_amount")
    elif transaction.amount >= 50000:
        score += 25
        reasons.append("elevated_amount")
    elif transaction.amount >= 10000:
        score += 10
        reasons.append("unusual_amount")

    if transaction.velocity >= 10:
        score += 30
        reasons.append("high_velocity")
    elif transaction.velocity >= 5:
        score += 18
        reasons.append("elevated_velocity")

    if transaction.failedLogins >= 5:
        score += 20
        reasons.append("brute_force_signals")
    elif transaction.failedLogins >= 2:
        score += 10
        reasons.append("failed_logins")

    if transaction.country.upper() not in {"IN", "US", "GB", "SG", "AE"}:
        score += 15
        reasons.append("unusual_country")

    if transaction.deviceId.lower().startswith(("new", "unknown", "risk")):
        score += 10
        reasons.append("new_device")

    if transaction.networkStatus == "DOWN":
        score += 20
        reasons.append("payment_network_timeout")
    elif transaction.networkStatus == "DEGRADED":
        score += 10
        reasons.append("payment_network_degraded")

    if not reasons:
        reasons.append("normal_behavior")

    return min(score, 100), reasons


def decision_for(score: int) -> Literal["ALLOW", "REVIEW", "BLOCK"]:
    if score >= BLOCK_THRESHOLD:
        return "BLOCK"
    if score >= REVIEW_THRESHOLD:
        return "REVIEW"
    return "ALLOW"


@app.middleware("http")
async def record_request_metrics(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    elapsed = time.perf_counter() - start
    path = request.url.path
    HTTP_LATENCY.labels(path=path).observe(elapsed)
    HTTP_REQUESTS.labels(
        method=request.method,
        path=path,
        status=str(response.status_code),
    ).inc()
    return response


@app.get("/health")
def health() -> dict:
    return {
        "status": "ok",
        "service": "fraud-api",
        "reviewThreshold": REVIEW_THRESHOLD,
        "blockThreshold": BLOCK_THRESHOLD,
    }


@app.post("/api/score", response_model=ScoreResponse)
def score_api(transaction: Transaction, x_api_token: str | None = Header(default=None)):
    require_token(x_api_token)
    risk_score, reasons = score_transaction(transaction)
    decision = decision_for(risk_score)
    trace_id = str(uuid.uuid4())

    result = {
        "transactionId": transaction.transactionId,
        "riskScore": risk_score,
        "decision": decision,
        "reasons": reasons,
        "traceId": trace_id,
        "amount": transaction.amount,
        "currency": transaction.currency.upper(),
        "country": transaction.country.upper(),
        "deviceId": transaction.deviceId,
        "customerId": transaction.customerId,
        "networkStatus": transaction.networkStatus,
        "createdAt": int(time.time()),
    }

    RECENT_TRANSACTIONS.appendleft(result)
    TRANSACTIONS.labels(decision=decision).inc()
    LATEST_RISK_SCORE.set(risk_score)
    print(
        json.dumps(
            {
                "event": "transaction_scored",
                "transactionId": transaction.transactionId,
                "decision": decision,
                "riskScore": risk_score,
                "traceId": trace_id,
                "reasons": reasons,
            }
        ),
        flush=True,
    )

    return ScoreResponse(**result)


@app.get("/api/recent")
def recent_transactions() -> dict:
    return {"items": list(RECENT_TRANSACTIONS), "count": len(RECENT_TRANSACTIONS)}


@app.get("/metrics")
def metrics() -> Response:
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
