# .devcontainer/Dockerfile
FROM mcr.microsoft.com/devcontainers/cpp:1-debian-12

# 1. Install uv (Copy exact binary from official image)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 2. Install System Python Headers
# Required for compiling C++ bindings against Python
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    python3-dev \
    && apt-get clean -y && rm -rf /var/lib/apt/lists/*  