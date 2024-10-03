# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.
import json

from logging import Logger
from typing import Any, Optional

from google.protobuf.json_format import MessageToDict
from grpc import ServicerContext, StatusCode

from session_dsm_pb2 import (
    DESCRIPTOR,
    RequestCreateGameSession,
    RequestTerminateGameSession,
    ResponseCreateGameSession,
    ResponseTerminateGameSession,
)
from session_dsm_pb2_grpc import SessionDsmServicer


class AsyncSessionDsmDemoService(SessionDsmServicer):
    full_name: str = DESCRIPTOR.services_by_name["SessionDsm"].full_name

    def __init__(
        self,
        logger: Optional[Logger] = None,
    ) -> None:
        self.logger = logger

    async def CreateGameSession(
        self, request: RequestCreateGameSession, context: ServicerContext
    ) -> ResponseCreateGameSession:
        self.log_payload(f"{self.CreateGameSession.__name__} request: %s", request)

        response = ResponseCreateGameSession()

        if len(request.requested_region) == 0:
            code: StatusCode = StatusCode.INVALID_ARGUMENT
            details: str = "Please provide requested region."
            await context.abort(code=code, details=details)

        selected_region = request.requested_region[0]

        response.client_version = request.client_version
        response.created_region = selected_region
        response.deployment = request.deployment
        response.game_mode = request.game_mode
        response.namespace = request.namespace
        response.region = selected_region
        response.session_data = request.session_data
        response.session_id = request.session_id
        response.source = "DEMO"
        response.status = "READY"

        response.ip = "10.10.10.11"
        response.port = 8080
        response.server_id = f"demo-local-{request.session_id}"

        self.log_payload(f"{self.CreateGameSession.__name__} response: %s", response)

        return response

    async def TerminateGameSession(
        self, request: RequestTerminateGameSession, context: ServicerContext
    ) -> ResponseTerminateGameSession:
        self.log_payload(f"{self.TerminateGameSession.__name__} request: %s", request)

        response = ResponseTerminateGameSession()

        response.namespace = request.namespace
        response.reason = ""
        response.session_id = request.session_id
        response.success = True

        self.log_payload(f"{self.TerminateGameSession.__name__} response: %s", response)

        return response

    # noinspection PyShadowingBuiltins
    def log_payload(self, format: str, payload: Any) -> None:
        if not self.logger:
            return

        payload_dict = MessageToDict(payload, preserving_proto_field_name=True)
        payload_json = json.dumps(payload_dict)

        self.logger.info(format % payload_json)


__all__ = [
    "AsyncSessionDsmDemoService",
]
