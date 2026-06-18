# FinGuard Lite Runbook

## Health Checks

```bash
curl http://localhost:8000/health
curl http://localhost:8000/metrics
kubectl get pods -n finguard
kubectl get hpa -n finguard
```

## Rollout

```bash
kubectl -n finguard rollout status deployment/fraud-api
kubectl -n finguard rollout history deployment/fraud-api
```

## Rollback

```bash
kubectl -n finguard rollout undo deployment/fraud-api
kubectl -n finguard rollout status deployment/fraud-api
```

## Logs

```bash
kubectl -n finguard logs deployment/fraud-api
kubectl -n logging get pods
```

## Metrics

```bash
kubectl -n monitoring get svc
kubectl -n monitoring port-forward svc/prometheus 9090:9090
kubectl -n monitoring port-forward svc/grafana 3000:3000
```

## Vault

```bash
kubectl -n vault get pods
kubectl -n vault port-forward svc/vault 8200:8200
export VAULT_ADDR=http://localhost:8200
export VAULT_TOKEN=finguard-root
vault kv get secret/finguard
```

## Common Fixes

If dashboard is online but transactions fail:

```bash
kubectl -n finguard get svc fraud-api
kubectl -n finguard logs deployment/dashboard
```

If pods are stuck pulling images:

```bash
kubectl -n finguard describe pod <pod-name>
aws ecr get-login-password --region ap-south-1
```

If Grafana is empty:

```bash
kubectl -n monitoring logs deployment/prometheus
kubectl -n monitoring port-forward svc/prometheus 9090:9090
```
