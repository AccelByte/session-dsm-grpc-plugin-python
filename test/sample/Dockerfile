FROM python:3.9-slim-bookworm
WORKDIR /data
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
RUN apt update && apt install -y bash curl git jq make xxd \
        && apt clean \
        && rm -rf /var/lib/apt/lists/*
RUN ARCH=$(uname -m | sed -e s/x86_64/amd64/ -e s/aarch64/arm64/) \
        && curl "https://download.docker.com/linux/debian/dists/bookworm/pool/stable/$ARCH/docker-ce-cli_23.0.6-1~debian.12~bookworm_$ARCH.deb" -o /tmp/docker-ce-cli.deb \
        && curl "https://download.docker.com/linux/debian/dists/bookworm/pool/stable/$ARCH/docker-buildx-plugin_0.11.2-1~debian.12~bookworm_$ARCH.deb" -o /tmp/docker-buildx-plugin.deb \
        && cat /tmp/docker-ce-cli.deb \
        && dpkg -i /tmp/docker-ce-cli.deb /tmp/docker-buildx-plugin.deb \
        && rm -f /tmp/docker-ce-cli.deb /tmp/docker-buildx-plugin.deb
COPY --from=ngrok/ngrok /bin/ngrok /bin/ngrok
