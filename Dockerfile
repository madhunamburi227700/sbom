# Use lightweight Python base
FROM python:3.12-slim

SHELL ["/bin/bash", "-c"]

# -------------------- BASE SETUP --------------------
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/root/.local/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    bash \
    curl \
    wget \
    gnupg \
    unzip \
    git \
    ca-certificates \
    build-essential \
    sudo \
    zip \
    && rm -rf /var/lib/apt/lists/*

# -------------------- UV SETUP --------------------
RUN curl -LsSf https://astral.sh/uv/install.sh | sh \
    && mv /root/.local/bin/uv /usr/local/bin/uv \
    && mv /root/.local/bin/uvx /usr/local/bin/uvx

# -------------------- TRIVY SETUP --------------------
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh \
    && mv ./bin/trivy /usr/local/bin/trivy \
    && rm -rf ./bin

# -------------------- WORKDIR & COPY --------------------
WORKDIR /app
COPY . /app

# -------------------- DEFAULT COMMAND --------------------
CMD ["bash"]
