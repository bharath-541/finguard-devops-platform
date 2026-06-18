#!/usr/bin/env bash
set -euo pipefail

NAMESPACE="${1:-finguard}"
AWS_REGION="${2:-ap-south-1}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

kubectl get namespace "${NAMESPACE}" >/dev/null 2>&1 || kubectl create namespace "${NAMESPACE}"

kubectl -n "${NAMESPACE}" delete secret ecr-pull-secret --ignore-not-found

kubectl -n "${NAMESPACE}" create secret docker-registry ecr-pull-secret \
  --docker-server="${REGISTRY}" \
  --docker-username=AWS \
  --docker-password="$(aws ecr get-login-password --region "${AWS_REGION}")"

echo "Created ECR pull secret in namespace ${NAMESPACE} for ${REGISTRY}"
