# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.

FROM --platform=$BUILDPLATFORM rvolosatovs/protoc:4.1.0 AS protoc
WORKDIR /build
COPY proto proto
COPY src src
RUN protoc  \
    --proto_path=proto/app \
    --grpc-python_out=src \
    --pyi_out=src \
    --python_out=src \
    session-dsm.proto

# Extend App
FROM python:3.9-slim-bullseye
ARG TARGETOS
ARG TARGETARCH
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt requirements.txt
RUN python -m pip install -r requirements.txt
COPY src .
COPY --from=protoc /build/src/session_dsm* .

# Plugin arch gRPC server port
EXPOSE 6565
# Prometheus /metrics web server port
EXPOSE 8080

ENTRYPOINT python -m app