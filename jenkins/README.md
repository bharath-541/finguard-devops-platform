# Local Jenkins Runner

This folder contains a local Jenkins image for running the project pipeline from Docker Desktop.

The image includes:

- Jenkins LTS
- Docker CLI
- AWS CLI
- kubectl
- Pipeline and Git plugins

## Start Jenkins

From the project root:

```bash
docker compose --profile ci up -d --build jenkins
```

Open Jenkins:

```text
http://localhost:8081
```

Get the first-time unlock password:

```bash
docker compose --profile ci logs jenkins
```

Look for the long password printed between the Jenkins setup lines.

## Required Local Files

The compose service mounts these local files into Jenkins:

- `~/.aws` for AWS CLI credentials
- `kubeconfig-finguard` for kubectl access to the k3s cluster
- `.jenkins_home` for Jenkins state and workspaces
- `/var/run/docker.sock` so Jenkins can build images through Docker Desktop

Before running the pipeline, confirm:

```bash
aws sts get-caller-identity
KUBECONFIG=./kubeconfig-finguard kubectl get nodes
docker ps
```

## Create the Jenkins Job

1. Click **New Item**.
2. Name it `finguard-devops-platform`.
3. Select **Pipeline**.
4. Under **Pipeline**, choose **Pipeline script from SCM**.
5. SCM: `Git`.
6. Repository URL:

```text
https://github.com/bharath-541/finguard-devops-platform.git
```

7. Branch:

```text
*/main
```

8. Script path:

```text
Jenkinsfile
```

9. Save, then click **Build with Parameters**.

Use:

```text
AWS_ACCOUNT_ID = your AWS account ID
AWS_REGION = ap-south-1
IMAGE_TAG = latest
DEPLOY_OBSERVABILITY = false
```

Use `DEPLOY_OBSERVABILITY=true` only when you want Jenkins to re-apply Prometheus, Grafana, Vault, and ELK as part of the run.

## Stop Jenkins

```bash
docker compose --profile ci down
```

Jenkins job history stays in `.jenkins_home`, which is ignored by Git.

