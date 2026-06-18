#!/usr/bin/env bash
set -euo pipefail

API_URL="${1:-http://localhost:8080/api/score}"
COUNT="${2:-25}"

for i in $(seq 1 "${COUNT}"); do
  curl -sS -X POST "${API_URL}" \
    -H "Content-Type: application/json" \
    -d "{
      \"transactionId\":\"spike-${i}-$(date +%s)\",
      \"amount\":145000,
      \"currency\":\"INR\",
      \"country\":\"BR\",
      \"deviceId\":\"new-device\",
      \"customerId\":\"cust-${i}\",
      \"failedLogins\":6,
      \"velocity\":12,
      \"networkStatus\":\"OK\"
    }" >/dev/null
done

echo "Sent ${COUNT} high-risk transactions to ${API_URL}"
