# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.

import json
import threading

from logging import Logger
from typing import Any, Optional

from google.protobuf.json_format import MessageToDict
from grpc import ServicerContext, StatusCode

import accelbyte_py_sdk.api.session as session
import accelbyte_py_sdk.api.session.models as session_models

from session_dsm_pb2 import (
    DESCRIPTOR,
    RequestCreateGameSession,
    RequestTerminateGameSession,
    ResponseCreateGameSession,
    ResponseCreateGameSessionAsync,
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

    async def CreateGameSessionAsync(
        self, request: RequestCreateGameSession, context: ServicerContext
    ) -> ResponseCreateGameSessionAsync:
        self.log_payload(f"{self.CreateGameSessionAsync.__name__} request: %s", request)

        response = ResponseCreateGameSessionAsync()
        response.message = "success"
        response.success = True

        threading.Timer(
            2,
            self._call_admin_update_ds_information,
            kwargs={
                "ip": "192.161.1.1",
                "port": 1223,
                "server_id": "123455",
                "description": "testing",
                "region": request.requested_region[0],
                "deployment": request.deployment,
                "session_id": request.session_id,
                "namespace": request.namespace,
            }
        ).start()

        self.log_payload(f"{self.CreateGameSessionAsync.__name__} response: %s", response)

        return response

    def _call_admin_update_ds_information(self, **kwargs):
        ip = kwargs.get("ip")
        port = kwargs.get("port")
        server_id = kwargs.get("server_id")
        description = kwargs.get("description")
        region = kwargs.get("region")
        deployment = kwargs.get("deployment")
        session_id = kwargs.get("session_id")
        namespace = kwargs.get("namespace")

        _, error = session.admin_update_ds_information(
            body=session_models.ApimodelsUpdateGamesessionDSInformationRequest.create(
                created_region=region,
                deployment=deployment,
                description=description,
                ip=ip,
                port=port,
                region=region,
                server_id=server_id,
                source="DEMO",
                status="AVAILABLE",
            ),
            session_id=session_id,
            namespace=namespace,
        )
        if error and self.logger:
            self.logger.warning(str(error))

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
