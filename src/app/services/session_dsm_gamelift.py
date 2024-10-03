# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.

import json

from logging import Logger
from typing import Any, Optional

import boto3

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


class AsyncSessionDsmGameLiftService(SessionDsmServicer):
    full_name: str = DESCRIPTOR.services_by_name["SessionDsm"].full_name

    def __init__(
        self, region_name: Optional[str] = None, logger: Optional[Logger] = None
    ) -> None:
        client_kwargs = {}
        if region_name:
            client_kwargs["region_name"] = region_name

        self.gamelift_client = boto3.client("gamelift", **client_kwargs)
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

        try:
            cgs_response = self.gamelift_client.create_game_sesion(
                AliasId=request.deployment,
                GameSessionData=request.session_data,
                IdempotencyToken=request.session_id,
                MaximumPlayerSessionCount=request.maximum_player,
                Location=selected_region,
            )

            if isinstance(cgs_response, dict):
                raise TypeError("Expected response to be a dict.")

            if "GameSession" not in cgs_response:
                raise ValueError("Expected 'GameSession' to be in response.")

            if isinstance(cgs_response["GameSession"], dict):
                raise TypeError("Expected response['GameSession'] to be a dict.")

            response.client_version = request.client_version
            response.game_mode = request.game_mode
            response.namespace = request.namespace
            response.region = selected_region
            response.session_data = request.session_data
            response.session_id = request.session_id
            response.source = "GAMELIFT"
            response.status = "READY"

            response.created_region = cgs_response["GameSession"]["Location"]
            response.deployment = cgs_response["GameSession"]["FleetId"]
            response.ip = cgs_response["GameSession"]["IpAddress"]
            response.port = cgs_response["GameSession"]["Port"]
            response.server_id = cgs_response["GameSession"]["GameSessionId"]

            self.log_payload(
                f"{self.CreateGameSession.__name__} response: %s", response
            )

        except Exception as exception:
            code: StatusCode = StatusCode.INTERNAL
            details: str = f"CreateGameSession Exception: {exception}"
            await context.abort(code=code, details=details)

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
    "AsyncSessionDsmGameLiftService",
]
