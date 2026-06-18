#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <ec2-public-ip> <private-key-path>"
  exit 1
fi

PUBLIC_IP="$1"
KEY_PATH="$2"
OUT_FILE="${3:-./kubeconfig-finguard}"

ssh -i "${KEY_PATH}" -o StrictHostKeyChecking=accept-new ubuntu@"${PUBLIC_IP}" \
  "sudo cat /etc/rancher/k3s/k3s.yaml" > "${OUT_FILE}"

python3 - "${OUT_FILE}" "${PUBLIC_IP}" <<'PY'
import pathlib
import sys

path = pathlib.Path(sys.argv[1])
public_ip = sys.argv[2]
content = path.read_text()
path.write_text(content.replace("https://127.0.0.1:6443", f"https://{public_ip}:6443"))
PY

echo "Wrote ${OUT_FILE}"
echo "Run: export KUBECONFIG=${OUT_FILE}"
