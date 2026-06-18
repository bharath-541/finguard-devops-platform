#!/usr/bin/env bash
set -euo pipefail

kubectl get pods -n finguard
kubectl get svc -n finguard
kubectl get ingress -n finguard
kubectl get pods -n monitoring
kubectl get pods -n logging
kubectl get pods -n vault
