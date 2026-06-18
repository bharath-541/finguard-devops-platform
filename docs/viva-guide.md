# Viva Guide

## One-Minute Explanation

FinGuard Lite is a simplified fraud intelligence platform. It receives payment transactions, calculates a fraud risk score, and returns ALLOW, REVIEW, or BLOCK. The DevOps part is the main focus: Terraform creates the AWS server, Docker packages the services, Kubernetes runs them with high availability, Jenkins automates deployment, Prometheus and Grafana monitor the system, ELK stores logs, and Vault demonstrates secret handling.

## Why This Design Is Simple

- One backend service keeps the business logic easy to understand.
- One dashboard keeps the demo visual.
- k3s gives real Kubernetes without EKS complexity.
- Optional profiles keep heavy tools separate from the basic demo.
- Scripts make viva scenarios repeatable.

## Questions You May Get

### Why Kubernetes?

Kubernetes gives self-healing, scaling, rolling updates, and rollback. If one fraud API pod fails, the service still works through the remaining pods.

### Why Terraform?

Terraform makes infrastructure repeatable. Instead of manually creating EC2, security groups, and ECR, the same code can create or destroy the environment.

### Why Jenkins?

Jenkins automates the delivery pipeline: test, build, push, deploy, and rollback. This reduces manual deployment mistakes.

### Why Prometheus and Grafana?

Prometheus collects metrics from `/metrics`. Grafana visualizes transaction rate, decision count, latency, and service health.

### Why ELK?

Logs are needed when fraud scoring fails or latency increases. Fluent Bit sends Kubernetes container logs to Elasticsearch, and Kibana helps search those logs.

### Why Vault?

Vault is for secrets such as tokens and thresholds. This demo runs Vault in dev mode to keep the viva simple. In production, Vault would use persistent storage, policies, and Kubernetes authentication.

### How Is Disaster Recovery Shown?

Use `scripts/pod_outage.sh` to delete API pods and show Kubernetes recreating them. Use `scripts/rollback.sh` to return to a previous deployment.

### How Is Fraud Spike Shown?

Use `scripts/load_spike.sh` or the dashboard button. The API blocks high-risk transactions and Prometheus/Grafana show increased traffic and risk decisions.

## Demo Order

1. Show dashboard.
2. Click Fraud Spike and explain ALLOW, REVIEW, BLOCK.
3. Open Prometheus/Grafana and show metrics.
4. Delete an API pod and show it recovering.
5. Run rollback command.
6. Show Jenkinsfile stages.
7. Show Terraform files and explain AWS creation.

## Keep This Line Ready

"This is a student-friendly version of a production design. The structure is production-oriented, but tools like Vault and ELK are kept lightweight so the full system can be executed and explained during evaluation."
