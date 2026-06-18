#!/bin/bash
set -euxo pipefail

apt-get update
apt-get install -y curl ca-certificates

TOKEN="$(curl -sS -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600" || true)"
if [ -n "${TOKEN}" ]; then
  PUBLIC_IP="$(curl -sS -H "X-aws-ec2-metadata-token: ${TOKEN}" http://169.254.169.254/latest/meta-data/public-ipv4 || true)"
else
  PUBLIC_IP="$(curl -sS http://169.254.169.254/latest/meta-data/public-ipv4 || true)"
fi

if [ -z "${PUBLIC_IP}" ]; then
  PUBLIC_IP="$(curl -sS https://checkip.amazonaws.com)"
fi

curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--write-kubeconfig-mode 644 --tls-san ${PUBLIC_IP}" sh -

until kubectl get nodes; do
  sleep 5
done

cat >/home/ubuntu/finguard-ready.txt <<READY
FinGuard k3s node is ready.
Copy kubeconfig with:
sudo cat /etc/rancher/k3s/k3s.yaml
Replace 127.0.0.1 with ${PUBLIC_IP}.
READY

chown ubuntu:ubuntu /home/ubuntu/finguard-ready.txt
