#!/usr/bin/env bash
set -euo pipefail

API_URL="${1:-http://localhost:8080/api/score}"

curl -sS -X POST "${API_URL}" \
  -H "Content-Type: application/json" \
  -d "{
    \"transactionId\":\"network-failure-$(date +%s)\",
    \"amount\":64000,
    \"currency\":\"INR\",
    \"country\":\"IN\",
    \"deviceId\":\"risk-edge\",
    \"customerId\":\"cust-network\",
    \"failedLogins\":2,
    \"velocity\":6,
    \"networkStatus\":\"DOWN\"
  }"

echo
