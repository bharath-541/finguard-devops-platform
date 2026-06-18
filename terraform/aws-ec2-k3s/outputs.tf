output "instance_public_ip" {
  description = "Public IP of the EC2 k3s node."
  value       = aws_instance.k3s.public_ip
}

output "app_url" {
  description = "Dashboard URL after Kubernetes manifests are deployed."
  value       = "http://${aws_instance.k3s.public_ip}"
}

output "prometheus_url" {
  description = "Prometheus NodePort URL."
  value       = "http://${aws_instance.k3s.public_ip}:30090"
}

output "grafana_url" {
  description = "Grafana NodePort URL."
  value       = "http://${aws_instance.k3s.public_ip}:30300"
}

output "kibana_url" {
  description = "Kibana NodePort URL."
  value       = "http://${aws_instance.k3s.public_ip}:30561"
}

output "fraud_api_ecr_url" {
  description = "ECR repository URL for fraud API image."
  value       = aws_ecr_repository.fraud_api.repository_url
}

output "dashboard_ecr_url" {
  description = "ECR repository URL for dashboard image."
  value       = aws_ecr_repository.dashboard.repository_url
}
