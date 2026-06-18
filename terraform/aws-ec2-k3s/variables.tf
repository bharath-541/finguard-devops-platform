variable "aws_region" {
  description = "AWS region for the FinGuard demo."
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Name prefix for AWS resources."
  type        = string
  default     = "finguard-lite"
}

variable "instance_type" {
  description = "EC2 instance type for the k3s node."
  type        = string
  default     = "m7i-flex.large"
}

variable "key_name" {
  description = "Existing AWS EC2 key pair name used for SSH."
  type        = string
}

variable "allowed_cidr" {
  description = "CIDR allowed to reach SSH, k3s API, and demo NodePorts. Use your public IP /32 for safer demos."
  type        = string
  default     = "0.0.0.0/0"
}
