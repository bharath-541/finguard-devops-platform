.PHONY: test local-up local-down local-observability local-security local-logging spike network k8s-base k8s-platform status

test:
	cd apps/fraud-api && PYTHONPATH=. pytest tests

local-up:
	docker compose up --build -d fraud-api dashboard

local-down:
	docker compose --profile observability --profile security --profile logging down

local-observability:
	docker compose --profile observability up -d prometheus grafana

local-security:
	docker compose --profile security up -d vault

local-logging:
	docker compose --profile logging up -d elasticsearch kibana

spike:
	./scripts/load_spike.sh

network:
	./scripts/network_failure.sh

k8s-platform:
	kubectl apply -k k8s/vault
	kubectl apply -k k8s/monitoring
	kubectl apply -k k8s/logging

k8s-base:
	kubectl apply -k k8s/base

status:
	./scripts/show_status.sh
