FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
      ca-certificates \
      curl \
      tar \
      unzip \
    && rm -rf /var/lib/apt/lists/*

RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
      amd64) docker_arch="x86_64" ;; \
      arm64) docker_arch="aarch64" ;; \
      *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
    esac; \
    curl --http1.1 --retry 5 --retry-delay 3 --retry-all-errors -fsSL "https://download.docker.com/linux/static/stable/${docker_arch}/docker-28.3.3.tgz" -o /tmp/docker.tgz; \
    tar -xzf /tmp/docker.tgz -C /tmp; \
    mv /tmp/docker/docker /usr/local/bin/docker; \
    chmod +x /usr/local/bin/docker; \
    rm -rf /tmp/docker /tmp/docker.tgz

RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
      amd64) buildx_arch="amd64" ;; \
      arm64) buildx_arch="arm64" ;; \
      *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
    esac; \
    mkdir -p /usr/local/lib/docker/cli-plugins; \
    curl --http1.1 --retry 5 --retry-delay 3 --retry-all-errors -fsSL "https://github.com/docker/buildx/releases/download/v0.30.1/buildx-v0.30.1.linux-${buildx_arch}" -o /usr/local/lib/docker/cli-plugins/docker-buildx; \
    chmod +x /usr/local/lib/docker/cli-plugins/docker-buildx

RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
      amd64) aws_arch="x86_64" ;; \
      arm64) aws_arch="aarch64" ;; \
      *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
    esac; \
    curl --http1.1 --retry 5 --retry-delay 3 --retry-all-errors -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-${aws_arch}.zip" -o /tmp/awscliv2.zip; \
    unzip -q /tmp/awscliv2.zip -d /tmp; \
    /tmp/aws/install; \
    rm -rf /tmp/aws /tmp/awscliv2.zip

RUN set -eux; \
    arch="$(dpkg --print-architecture)"; \
    case "$arch" in \
      amd64) kubectl_arch="amd64" ;; \
      arm64) kubectl_arch="arm64" ;; \
      *) echo "Unsupported architecture: $arch" >&2; exit 1 ;; \
    esac; \
    curl --http1.1 --retry 5 --retry-delay 3 --retry-all-errors -fsSL "https://dl.k8s.io/release/v1.31.4/bin/linux/${kubectl_arch}/kubectl" -o /usr/local/bin/kubectl; \
    chmod +x /usr/local/bin/kubectl

COPY plugins.txt /usr/share/jenkins/ref/plugins.txt
RUN jenkins-plugin-cli --plugin-file /usr/share/jenkins/ref/plugins.txt
