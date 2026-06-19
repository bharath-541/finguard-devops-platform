# Postman Demo

Import this collection into Postman:

```text
docs/postman/finguard-api.postman_collection.json
```

The collection uses this variable:

```text
base_url = http://3.110.140.20
prometheus_url = http://3.110.140.20:30090
```

Requests included:

- Health Check
- Score Transaction - Low Risk ALLOW
- Score Transaction - Medium Risk REVIEW
- Score Transaction - High Risk BLOCK
- Score Transaction - Payment Network Failure
- Recent Transactions
- Prometheus Metrics

Demo order:

1. Run `Health Check`.
2. Run `Score Transaction - Low Risk ALLOW`.
3. Run `Score Transaction - Medium Risk REVIEW`.
4. Run `Score Transaction - High Risk BLOCK`.
5. Run `Recent Transactions`.
6. Run `Prometheus Metrics`.

The `Prometheus Metrics` request uses:

```text
GET {{prometheus_url}}/api/v1/query?query=finguard_transactions_total
```

This returns JSON from Prometheus and proves application metrics are available.

Explanation:

> Postman is used to demonstrate live backend API execution. The fraud API accepts transaction data, calculates risk score, returns a fraud decision, and exposes metrics for Prometheus.
