#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-finguard}"

kubectl -n "${NAMESPACE}" rollout undo deployment/fraud-api
kubectl -n "${NAMESPACE}" rollout status deployment/fraud-api --timeout=180s
