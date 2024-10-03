# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import session_dsm_pb2 as session__dsm__pb2


class SessionDsmStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.CreateGameSession = channel.unary_unary(
                '/accelbyte.session.sessiondsm.SessionDsm/CreateGameSession',
                request_serializer=session__dsm__pb2.RequestCreateGameSession.SerializeToString,
                response_deserializer=session__dsm__pb2.ResponseCreateGameSession.FromString,
                )
        self.TerminateGameSession = channel.unary_unary(
                '/accelbyte.session.sessiondsm.SessionDsm/TerminateGameSession',
                request_serializer=session__dsm__pb2.RequestTerminateGameSession.SerializeToString,
                response_deserializer=session__dsm__pb2.ResponseTerminateGameSession.FromString,
                )


class SessionDsmServicer(object):
    """Missing associated documentation comment in .proto file."""

    def CreateGameSession(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def TerminateGameSession(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_SessionDsmServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'CreateGameSession': grpc.unary_unary_rpc_method_handler(
                    servicer.CreateGameSession,
                    request_deserializer=session__dsm__pb2.RequestCreateGameSession.FromString,
                    response_serializer=session__dsm__pb2.ResponseCreateGameSession.SerializeToString,
            ),
            'TerminateGameSession': grpc.unary_unary_rpc_method_handler(
                    servicer.TerminateGameSession,
                    request_deserializer=session__dsm__pb2.RequestTerminateGameSession.FromString,
                    response_serializer=session__dsm__pb2.ResponseTerminateGameSession.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'accelbyte.session.sessiondsm.SessionDsm', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class SessionDsm(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def CreateGameSession(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/accelbyte.session.sessiondsm.SessionDsm/CreateGameSession',
            session__dsm__pb2.RequestCreateGameSession.SerializeToString,
            session__dsm__pb2.ResponseCreateGameSession.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def TerminateGameSession(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/accelbyte.session.sessiondsm.SessionDsm/TerminateGameSession',
            session__dsm__pb2.RequestTerminateGameSession.SerializeToString,
            session__dsm__pb2.ResponseTerminateGameSession.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
