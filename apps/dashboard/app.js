const API_BASE = window.FINGUARD_CONFIG?.apiBase || "/api";

const state = {
  items: [],
  latencies: [],
  eventTrail: [],
  counts: {
    ALLOW: 0,
    REVIEW: 0,
    BLOCK: 0,
  },
};

const els = {
  totalScored: document.querySelector("#totalScored"),
  blockedCount: document.querySelector("#blockedCount"),
  latencyValue: document.querySelector("#latencyValue"),
  podHealth: document.querySelector("#podHealth"),
  apiStatus: document.querySelector("#apiStatus"),
  rows: document.querySelector("#transactionRows"),
  allowCount: document.querySelector("#allowCount"),
  reviewCount: document.querySelector("#reviewCount"),
  blockCount: document.querySelector("#blockCount"),
  allowBar: document.querySelector("#allowBar"),
  reviewBar: document.querySelector("#reviewBar"),
  blockBar: document.querySelector("#blockBar"),
  rolloutState: document.querySelector("#rolloutState"),
  vaultState: document.querySelector("#vaultState"),
  loggingState: document.querySelector("#loggingState"),
  k8sState: document.querySelector("#k8sState"),
  eventTrail: document.querySelector("#eventTrail"),
};

function formatAmount(item) {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: item.currency || "INR",
    maximumFractionDigits: 0,
  }).format(item.amount || 0);
}

function addEvent(message) {
  const stamp = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" });
  state.eventTrail.unshift(`${stamp} - ${message}`);
  state.eventTrail = state.eventTrail.slice(0, 5);
  els.eventTrail.innerHTML = state.eventTrail.map((entry) => `<li>${entry}</li>`).join("");
}

function decisionClass(decision) {
  return String(decision || "ALLOW").toLowerCase();
}

function updateMetrics() {
  const total = state.items.length;
  const counts = state.items.reduce(
    (acc, item) => {
      acc[item.decision] = (acc[item.decision] || 0) + 1;
      return acc;
    },
    { ALLOW: 0, REVIEW: 0, BLOCK: 0 },
  );

  state.counts = counts;
  els.totalScored.textContent = String(total);
  els.blockedCount.textContent = String(counts.BLOCK);
  els.allowCount.textContent = String(counts.ALLOW);
  els.reviewCount.textContent = String(counts.REVIEW);
  els.blockCount.textContent = String(counts.BLOCK);

  const averageLatency = state.latencies.length
    ? Math.round(state.latencies.reduce((sum, value) => sum + value, 0) / state.latencies.length)
    : 0;
  els.latencyValue.textContent = `${averageLatency} ms`;

  const denominator = Math.max(total, 1);
  els.allowBar.style.width = `${(counts.ALLOW / denominator) * 100}%`;
  els.reviewBar.style.width = `${(counts.REVIEW / denominator) * 100}%`;
  els.blockBar.style.width = `${(counts.BLOCK / denominator) * 100}%`;
}

function renderRows() {
  if (!state.items.length) {
    els.rows.innerHTML = `<tr><td class="empty-row" colspan="6">Waiting for scored transactions</td></tr>`;
    return;
  }

  els.rows.innerHTML = state.items
    .slice(0, 12)
    .map((item) => {
      const type = decisionClass(item.decision);
      const reason = Array.isArray(item.reasons) ? item.reasons[0] : "normal_behavior";
      return `
        <tr>
          <td>${item.transactionId}</td>
          <td>${formatAmount(item)}</td>
          <td>${item.country || "IN"}</td>
          <td><span class="risk-pill ${type}">${item.riskScore}</span></td>
          <td><span class="decision ${type}">${item.decision}</span></td>
          <td>${reason}</td>
        </tr>
      `;
    })
    .join("");
}

async function refreshRecent() {
  const response = await fetch(`${API_BASE}/recent`);
  if (!response.ok) {
    throw new Error("Recent transaction request failed");
  }
  const body = await response.json();
  state.items = body.items || [];
  renderRows();
  updateMetrics();
}

async function refreshHealth() {
  try {
    const response = await fetch("/health").catch(() => fetch(`${API_BASE.replace(/\/api$/, "")}/health`));
    if (!response.ok) {
      throw new Error("Health check failed");
    }
    els.apiStatus.textContent = "API online";
    els.apiStatus.className = "status-chip";
    els.podHealth.textContent = "3/3 ready";
    els.k8sState.textContent = "3 API pods";
  } catch (error) {
    els.apiStatus.textContent = "API offline";
    els.apiStatus.className = "status-chip is-down";
    els.podHealth.textContent = "degraded";
    els.k8sState.textContent = "check cluster";
  }
}

function makeTransaction(kind) {
  const id = `${kind}-${Date.now()}-${Math.floor(Math.random() * 999)}`;
  const safeCustomer = Math.floor(Math.random() * 90) + 10;

  if (kind === "fraud") {
    return {
      transactionId: id,
      amount: 100000 + Math.floor(Math.random() * 80000),
      currency: "INR",
      country: ["BR", "NG", "RU"][Math.floor(Math.random() * 3)],
      deviceId: "new-device",
      customerId: `cust-${safeCustomer}`,
      failedLogins: 5 + Math.floor(Math.random() * 5),
      velocity: 10 + Math.floor(Math.random() * 12),
      networkStatus: "OK",
    };
  }

  if (kind === "network") {
    return {
      transactionId: id,
      amount: 64000,
      currency: "INR",
      country: "IN",
      deviceId: "risk-edge",
      customerId: `cust-${safeCustomer}`,
      failedLogins: 2,
      velocity: 6,
      networkStatus: "DOWN",
    };
  }

  return {
    transactionId: id,
    amount: 950 + Math.floor(Math.random() * 7000),
    currency: "INR",
    country: "IN",
    deviceId: "device-known",
    customerId: `cust-${safeCustomer}`,
    failedLogins: 0,
    velocity: 1 + Math.floor(Math.random() * 3),
    networkStatus: "OK",
  };
}

async function scoreTransaction(transaction) {
  const start = performance.now();
  const response = await fetch(`${API_BASE}/score`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(transaction),
  });
  const latency = performance.now() - start;
  state.latencies.unshift(latency);
  state.latencies = state.latencies.slice(0, 20);

  if (!response.ok) {
    throw new Error("Score request failed");
  }

  return response.json();
}

async function runScenario(kind, count, eventText) {
  try {
    await Promise.all(Array.from({ length: count }, () => scoreTransaction(makeTransaction(kind))));
    await refreshRecent();
    await refreshHealth();
    addEvent(eventText);
  } catch (error) {
    addEvent("API request failed");
    await refreshHealth();
  }
}

async function seedInitialData() {
  await runScenario("safe", 3, "baseline transactions scored");
  await runScenario("fraud", 1, "initial high-risk signal blocked");
}

document.querySelector("#fraudSpikeBtn").addEventListener("click", () => {
  runScenario("fraud", 8, "fraud spike generated");
});

document.querySelector("#networkFailureBtn").addEventListener("click", () => {
  runScenario("network", 1, "payment network failure scored");
});

document.querySelector("#podOutageBtn").addEventListener("click", async () => {
  els.podHealth.textContent = "2/3 ready";
  els.k8sState.textContent = "self-healing";
  addEvent("pod outage drill started");
  setTimeout(() => {
    els.podHealth.textContent = "3/3 ready";
    els.k8sState.textContent = "3 API pods";
    addEvent("pod replacement ready");
  }, 1600);
});

document.querySelector("#rollbackBtn").addEventListener("click", () => {
  els.rolloutState.textContent = "rolled back";
  addEvent("release rollback completed");
  setTimeout(() => {
    els.rolloutState.textContent = "stable";
  }, 1800);
});

async function boot() {
  renderRows();
  await refreshHealth();
  try {
    await refreshRecent();
    if (!state.items.length) {
      await seedInitialData();
    }
  } catch (error) {
    addEvent("dashboard waiting for API");
  }
}

boot();
setInterval(refreshHealth, 8000);
