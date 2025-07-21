# Copyright (c) 2025 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.

import asyncio
import logging
from logging import Logger
from typing import List, Optional

from environs import Env

from accelbyte_py_sdk import get_version
from accelbyte_py_sdk.core import (
    AccelByteSDK,
    DictConfigRepository,
    InMemoryTokenRepository,
    HttpxHttpClient,
)
from accelbyte_py_sdk.services import auth as auth_service

from accelbyte_grpc_plugin.app import (
    App,
    AppOption,
    AppOptionGRPCInterceptor,
    AppOptionGRPCService,
)
from accelbyte_grpc_plugin.utils import instrument_sdk_http_client

from session_dsm_pb2_grpc import add_SessionDsmServicer_to_server
from .services.session_dsm_demo import AsyncSessionDsmDemoService
from .services.session_dsm_gamelift import AsyncSessionDsmGameLiftService
from .services.session_dsm_gcp import AsyncSessionDsmGcpService
from .utils import create_env

DEFAULT_APP_PORT: int = 6565

DEFAULT_AB_BASE_URL: str = "https://test.accelbyte.io"
DEFAULT_AB_NAMESPACE: str = "accelbyte"

DEFAULT_ENABLE_HEALTH_CHECK: bool = True
DEFAULT_ENABLE_PROMETHEUS: bool = True
DEFAULT_ENABLE_REFLECTION: bool = True
DEFAULT_ENABLE_ZIPKIN: bool = True

DEFAULT_PLUGIN_GRPC_SERVER_AUTH_ENABLED: bool = True
DEFAULT_PLUGIN_GRPC_SERVER_AUTH_RESOURCE: Optional[str] = None
DEFAULT_PLUGIN_GRPC_SERVER_AUTH_ACTION: Optional[int] = None

DEFAULT_PLUGIN_GRPC_SERVER_LOGGING_ENABLED: bool = False
DEFAULT_PLUGIN_GRPC_SERVER_METRICS_ENABLED: bool = True


async def main(**kwargs) -> None:
    env = create_env(**kwargs)

    port: int = env.int("PORT", DEFAULT_APP_PORT)

    logger = logging.getLogger("app")
    logger.setLevel(logging.INFO)
    logger.addHandler(logging.StreamHandler())

    config = DictConfigRepository(dict(env.dump()))
    token = InMemoryTokenRepository()
    http = HttpxHttpClient()
    http.client.follow_redirects = True

    sdk = AccelByteSDK()
    sdk.initialize(
        options={
            "config": config,
            "token": token,
            "http": http,
        }
    )

    instrument_sdk_http_client(sdk=sdk, logger=logger)

    _, error = await auth_service.login_client_async(sdk=sdk)
    if error:
        raise Exception(str(error))

    sdk.timer = auth_service.LoginClientTimer(5, refresh_rate=0.8, repeats=-1, autostart=True, sdk=sdk)

    options = create_options(sdk=sdk, env=env, logger=logger)

    ds_provider = env("DS_PROVIDER", "DEMO")
    service_full_name = ""
    service = None
    if ds_provider == "GAMELIFT":
        service_full_name = AsyncSessionDsmGameLiftService.full_name
        service = AsyncSessionDsmGameLiftService(
            region_name=env("AWS_REGION", env("GAMELIFT_REGION")),
            logger=logger,
        )
    elif ds_provider == "GCP":
        service_full_name = AsyncSessionDsmGcpService.full_name
        service = AsyncSessionDsmGcpService(
            service_account_file=env("GCP_SERVICE_ACCOUNT_FILE"),
            project_id=env("GCP_PROJECT_ID"),
            machine_type=env("GCP_MACHINE_TYPE", "e2-micro"),
            network_name=env("GCP_NETWORK", "public"),
            repository_name=env("GCP_REPOSITORY"),
            image_open_port=env.int("GCP_IMAGE_OPEN_PORT", 8080),
            max_retries=env.int("GCP_RETRY", 3),
            retry_interval=env.float("GCP_WAIT_GET_IP", 1.0),
            logger=logger,
        )
    elif ds_provider == "DEMO":
        service_full_name = AsyncSessionDsmDemoService.full_name
        service = AsyncSessionDsmDemoService(logger=logger)
    else:
        raise NotImplementedError(ds_provider)

    logger.info(f"DS provider: {ds_provider}")

    options.append(
        AppOptionGRPCService(
            full_name=service_full_name,
            service=service,
            add_service_fn=add_SessionDsmServicer_to_server,
        )
    )

    app = App(port=port, env=env, logger=logger, options=options)

    logger.info(f"using {get_version(latest=True, full=True)}")

    await app.run()


def create_options(sdk: AccelByteSDK, env: Env, logger: Logger) -> List[AppOption]:
    options: List[AppOption] = []

    with env.prefixed("AB_"):
        namespace = env.str("NAMESPACE", DEFAULT_AB_NAMESPACE)

    with env.prefixed("ENABLE_"):
        if env.bool("HEALTH_CHECK", DEFAULT_ENABLE_HEALTH_CHECK):
            from accelbyte_grpc_plugin.options.grpc_health_check import (
                AppOptionGRPCHealthCheck,
            )

            options.append(AppOptionGRPCHealthCheck())
        if env.bool("PROMETHEUS", DEFAULT_ENABLE_PROMETHEUS):
            from accelbyte_grpc_plugin.options.prometheus import (
                AppOptionPrometheus
            )

            options.append(AppOptionPrometheus())
        if env.bool("REFLECTION", DEFAULT_ENABLE_REFLECTION):
            from accelbyte_grpc_plugin.options.grpc_reflection import (
                AppOptionGRPCReflection,
            )

            options.append(AppOptionGRPCReflection())
        if env.bool("ZIPKIN", DEFAULT_ENABLE_ZIPKIN):
            from accelbyte_grpc_plugin.options.zipkin import (
                AppOptionZipkin
            )

            options.append(AppOptionZipkin())

    with env.prefixed("PLUGIN_GRPC_SERVER_"):
        with env.prefixed("AUTH_"):
            if env.bool("ENABLED", DEFAULT_PLUGIN_GRPC_SERVER_AUTH_ENABLED):
                from accelbyte_py_sdk.token_validation.caching import CachingTokenValidator
                from accelbyte_grpc_plugin.interceptors.authorization import AuthorizationServerInterceptor

                options.append(
                    AppOptionGRPCInterceptor(
                        interceptor=AuthorizationServerInterceptor(
                            token_validator=CachingTokenValidator(sdk=sdk),
                            resource=env.str(
                                "RESOURCE", DEFAULT_PLUGIN_GRPC_SERVER_AUTH_RESOURCE
                            ),
                            action=env.int(
                                "ACTION", DEFAULT_PLUGIN_GRPC_SERVER_AUTH_ACTION
                            ),
                            namespace=namespace,
                        )
                    )
                )
        if env.bool("LOGGING_ENABLED", DEFAULT_PLUGIN_GRPC_SERVER_LOGGING_ENABLED):
            from accelbyte_grpc_plugin.interceptors.logging import (
                LoggingServerInterceptor,
            )

            options.append(
                AppOptionGRPCInterceptor(
                    interceptor=LoggingServerInterceptor(logger=logger)
                )
            )

        if env.bool("METRICS_ENABLED", DEFAULT_PLUGIN_GRPC_SERVER_METRICS_ENABLED):
            from accelbyte_grpc_plugin.interceptors.metrics import (
                MetricsServerInterceptor,
            )

            options.append(
                AppOptionGRPCInterceptor(interceptor=MetricsServerInterceptor())
            )

    return options


def run() -> None:
    asyncio.run(main())


if __name__ == "__main__":
    run()
