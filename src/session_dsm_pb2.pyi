from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from collections.abc import Iterable as _Iterable
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RequestTerminateGameSession(_message.Message):
    __slots__ = ("session_id", "namespace", "zone")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    ZONE_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    namespace: str
    zone: str
    def __init__(self, session_id: _Optional[str] = ..., namespace: _Optional[str] = ..., zone: _Optional[str] = ...) -> None: ...

class ResponseTerminateGameSession(_message.Message):
    __slots__ = ("session_id", "namespace", "success", "reason")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    namespace: str
    success: bool
    reason: str
    def __init__(self, session_id: _Optional[str] = ..., namespace: _Optional[str] = ..., success: bool = ..., reason: _Optional[str] = ...) -> None: ...

class RequestCreateGameSession(_message.Message):
    __slots__ = ("session_id", "namespace", "deployment", "session_data", "requested_region", "maximum_player", "client_version", "game_mode", "secret")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    SESSION_DATA_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_REGION_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_PLAYER_FIELD_NUMBER: _ClassVar[int]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    GAME_MODE_FIELD_NUMBER: _ClassVar[int]
    SECRET_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    namespace: str
    deployment: str
    session_data: str
    requested_region: _containers.RepeatedScalarFieldContainer[str]
    maximum_player: int
    client_version: str
    game_mode: str
    secret: str
    def __init__(self, session_id: _Optional[str] = ..., namespace: _Optional[str] = ..., deployment: _Optional[str] = ..., session_data: _Optional[str] = ..., requested_region: _Optional[_Iterable[str]] = ..., maximum_player: _Optional[int] = ..., client_version: _Optional[str] = ..., game_mode: _Optional[str] = ..., secret: _Optional[str] = ...) -> None: ...

class ResponseCreateGameSession(_message.Message):
    __slots__ = ("session_id", "namespace", "session_data", "status", "ip", "port", "server_id", "source", "deployment", "region", "client_version", "game_mode", "created_region")
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SESSION_DATA_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    GAME_MODE_FIELD_NUMBER: _ClassVar[int]
    CREATED_REGION_FIELD_NUMBER: _ClassVar[int]
    session_id: str
    namespace: str
    session_data: str
    status: str
    ip: str
    port: int
    server_id: str
    source: str
    deployment: str
    region: str
    client_version: str
    game_mode: str
    created_region: str
    def __init__(self, session_id: _Optional[str] = ..., namespace: _Optional[str] = ..., session_data: _Optional[str] = ..., status: _Optional[str] = ..., ip: _Optional[str] = ..., port: _Optional[int] = ..., server_id: _Optional[str] = ..., source: _Optional[str] = ..., deployment: _Optional[str] = ..., region: _Optional[str] = ..., client_version: _Optional[str] = ..., game_mode: _Optional[str] = ..., created_region: _Optional[str] = ...) -> None: ...

class ResponseCreateGameSessionAsync(_message.Message):
    __slots__ = ("success", "message")
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    success: bool
    message: str
    def __init__(self, success: bool = ..., message: _Optional[str] = ...) -> None: ...
