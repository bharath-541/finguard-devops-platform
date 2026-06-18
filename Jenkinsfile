pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  parameters {
    string(name: 'AWS_ACCOUNT_ID', defaultValue: '123456789012', description: 'AWS account ID that owns the ECR repositories')
    string(name: 'AWS_REGION', defaultValue: 'ap-south-1', description: 'AWS region used by Terraform')
    string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'Image tag to build and deploy')
    booleanParam(name: 'DEPLOY_OBSERVABILITY', defaultValue: true, description: 'Deploy Prometheus, Grafana, Vault, and ELK manifests')
  }

  environment {
    PROJECT_NAME = 'finguard-lite'
    KUBE_NAMESPACE = 'finguard'
  }

  stages {
    stage('Test API') {
      steps {
        sh '''
          docker run --rm \
            -v "$PWD/apps/fraud-api:/app" \
            -w /app \
            python:3.12-slim \
            sh -c "pip install --no-cache-dir -r requirements.txt && PYTHONPATH=. pytest tests"
        '''
      }
    }

    stage('Build Images') {
      steps {
        sh '''
          ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
          docker buildx version
          docker buildx build --platform linux/amd64 \
            -t "${ECR_REGISTRY}/${PROJECT_NAME}-fraud-api:${IMAGE_TAG}" \
            --load \
            apps/fraud-api
          docker buildx build --platform linux/amd64 \
            -t "${ECR_REGISTRY}/${PROJECT_NAME}-dashboard:${IMAGE_TAG}" \
            --load \
            apps/dashboard
        '''
      }
    }

    stage('Push to ECR') {
      steps {
        sh '''
          ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
          aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_REGISTRY}"

          docker push "${ECR_REGISTRY}/${PROJECT_NAME}-fraud-api:${IMAGE_TAG}"
          docker push "${ECR_REGISTRY}/${PROJECT_NAME}-dashboard:${IMAGE_TAG}"
        '''
      }
    }

    stage('Deploy Platform Addons') {
      when {
        expression { return params.DEPLOY_OBSERVABILITY }
      }
      steps {
        sh '''
          kubectl apply -k k8s/vault
          kubectl apply -k k8s/monitoring
          kubectl apply -k k8s/logging
        '''
      }
    }

    stage('Deploy FinGuard') {
      steps {
        sh '''
          ECR_REGISTRY="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
          API_IMAGE="${ECR_REGISTRY}/${PROJECT_NAME}-fraud-api:${IMAGE_TAG}"
          DASHBOARD_IMAGE="${ECR_REGISTRY}/${PROJECT_NAME}-dashboard:${IMAGE_TAG}"

          ./scripts/create_ecr_pull_secret.sh "${KUBE_NAMESPACE}" "${AWS_REGION}"
          kubectl apply -k k8s/base
          kubectl -n "${KUBE_NAMESPACE}" set image deployment/fraud-api fraud-api="${API_IMAGE}"
          kubectl -n "${KUBE_NAMESPACE}" set image deployment/dashboard dashboard="${DASHBOARD_IMAGE}"
          kubectl -n "${KUBE_NAMESPACE}" rollout status deployment/fraud-api --timeout=180s
          kubectl -n "${KUBE_NAMESPACE}" rollout status deployment/dashboard --timeout=180s
        '''
      }
    }
  }

  post {
    failure {
      sh '''
        kubectl -n "${KUBE_NAMESPACE}" rollout undo deployment/fraud-api || true
        kubectl -n "${KUBE_NAMESPACE}" rollout undo deployment/dashboard || true
      '''
    }
  }
}
