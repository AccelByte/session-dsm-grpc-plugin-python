from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class RequestCreateGameSession(_message.Message):
    __slots__ = ["client_version", "deployment", "game_mode", "maximum_player", "namespace", "requested_region", "session_data", "session_id"]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    GAME_MODE_FIELD_NUMBER: _ClassVar[int]
    MAXIMUM_PLAYER_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    REQUESTED_REGION_FIELD_NUMBER: _ClassVar[int]
    SESSION_DATA_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    client_version: str
    deployment: str
    game_mode: str
    maximum_player: int
    namespace: str
    requested_region: _containers.RepeatedScalarFieldContainer[str]
    session_data: str
    session_id: str
    def __init__(self, session_id: _Optional[str] = ..., namespace: _Optional[str] = ..., deployment: _Optional[str] = ..., session_data: _Optional[str] = ..., requested_region: _Optional[_Iterable[str]] = ..., maximum_player: _Optional[int] = ..., client_version: _Optional[str] = ..., game_mode: _Optional[str] = ...) -> None: ...

class RequestTerminateGameSession(_message.Message):
    __slots__ = ["namespace", "session_id", "zone"]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    ZONE_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    session_id: str
    zone: str
    def __init__(self, session_id: _Optional[str] = ..., namespace: _Optional[str] = ..., zone: _Optional[str] = ...) -> None: ...

class ResponseCreateGameSession(_message.Message):
    __slots__ = ["client_version", "created_region", "deployment", "game_mode", "ip", "namespace", "port", "region", "server_id", "session_data", "session_id", "source", "status"]
    CLIENT_VERSION_FIELD_NUMBER: _ClassVar[int]
    CREATED_REGION_FIELD_NUMBER: _ClassVar[int]
    DEPLOYMENT_FIELD_NUMBER: _ClassVar[int]
    GAME_MODE_FIELD_NUMBER: _ClassVar[int]
    IP_FIELD_NUMBER: _ClassVar[int]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    REGION_FIELD_NUMBER: _ClassVar[int]
    SERVER_ID_FIELD_NUMBER: _ClassVar[int]
    SESSION_DATA_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    STATUS_FIELD_NUMBER: _ClassVar[int]
    client_version: str
    created_region: str
    deployment: str
    game_mode: str
    ip: str
    namespace: str
    port: int
    region: str
    server_id: str
    session_data: str
    session_id: str
    source: str
    status: str
    def __init__(self, session_id: _Optional[str] = ..., namespace: _Optional[str] = ..., session_data: _Optional[str] = ..., status: _Optional[str] = ..., ip: _Optional[str] = ..., port: _Optional[int] = ..., server_id: _Optional[str] = ..., source: _Optional[str] = ..., deployment: _Optional[str] = ..., region: _Optional[str] = ..., client_version: _Optional[str] = ..., game_mode: _Optional[str] = ..., created_region: _Optional[str] = ...) -> None: ...

class ResponseTerminateGameSession(_message.Message):
    __slots__ = ["namespace", "reason", "session_id", "success"]
    NAMESPACE_FIELD_NUMBER: _ClassVar[int]
    REASON_FIELD_NUMBER: _ClassVar[int]
    SESSION_ID_FIELD_NUMBER: _ClassVar[int]
    SUCCESS_FIELD_NUMBER: _ClassVar[int]
    namespace: str
    reason: str
    session_id: str
    success: bool
    def __init__(self, session_id: _Optional[str] = ..., namespace: _Optional[str] = ..., success: bool = ..., reason: _Optional[str] = ...) -> None: ...
