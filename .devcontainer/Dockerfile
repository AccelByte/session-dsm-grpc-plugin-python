# Development container for AccelByte Extend Service Extension
FROM ubuntu:26.04

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

ARG PROTOC_VERSION=21.9
ARG PYTHON_VERSION=3.14

# Configure apt and install packages
RUN apt-get update \
    && apt-get -y install --no-install-recommends \
    #
    # Install essential development tools
    build-essential \
    ca-certificates \
    sudo \
    unzip \
    wget \
    #
    # Install Python and pip
    python${PYTHON_VERSION} \
    python${PYTHON_VERSION}-dev \
    python${PYTHON_VERSION}-venv \
    python3-pip \
    #
    # Install Protocol Buffers compiler
    && wget -O protoc.zip https://github.com/protocolbuffers/protobuf/releases/download/v${PROTOC_VERSION}/protoc-${PROTOC_VERSION}-linux-x86_64.zip \
    && unzip protoc.zip -d /usr/local \
    && rm protoc.zip \
    && chmod +x /usr/local/bin/protoc \
    #
    # Install AGS CLI. CARGO_HOME puts the binary in /usr/local/bin, which is
    # already on PATH for every user, so no shell profile has to change.
    && wget --https-only -qO /tmp/ags-installer.sh https://github.com/AccelByte/accelbyte-ags-cli/releases/latest/download/accelbyte-ags-cli-installer.sh \
    && CARGO_HOME=/usr/local ACCELBYTE_AGS_CLI_NO_MODIFY_PATH=1 sh /tmp/ags-installer.sh \
    && rm /tmp/ags-installer.sh \
    #
    # Clean up
    && apt-get autoremove -y \
    && apt-get clean -y \
    && rm -rf /var/lib/apt/lists/*

# Set up Python symlinks
RUN ln -sf /usr/bin/python${PYTHON_VERSION} /usr/local/bin/python3 \
    && ln -sf /usr/bin/python${PYTHON_VERSION} /usr/local/bin/python \
    && ln -sf /usr/bin/pip3 /usr/local/bin/pip

# Create a non-root user. Ubuntu 26.04 already ships uid/gid 1000 as
# "ubuntu", so reuse that account instead of failing on groupadd.
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID

RUN if getent passwd "$USER_UID" >/dev/null; then \
        EXISTING_USER="$(getent passwd "$USER_UID" | cut -d: -f1)"; \
        if [ "$EXISTING_USER" != "$USERNAME" ]; then \
            usermod -l "$USERNAME" "$EXISTING_USER"; \
        fi; \
        EXISTING_GROUP="$(getent group "$USER_GID" | cut -d: -f1)"; \
        if [ "$EXISTING_GROUP" != "$USERNAME" ]; then \
            groupmod -n "$USERNAME" "$EXISTING_GROUP"; \
        fi; \
        usermod -d "/home/$USERNAME" -m "$USERNAME"; \
    else \
        groupadd --gid "$USER_GID" "$USERNAME"; \
        useradd --uid "$USER_UID" --gid "$USER_GID" -m "$USERNAME"; \
    fi \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Switch to non-root user
USER $USERNAME

# Install Python development tools
# PEP 668: Ubuntu 26.04's system interpreter is externally managed, and
# --user alone does not exempt the install.
RUN pip install --user --break-system-packages \
    grpcio-tools==1.76.0 mypy-protobuf==4.0.0 fillenv==1.0.0

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

WORKDIR /workspace
