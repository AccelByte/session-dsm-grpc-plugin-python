# Copyright (c) 2021 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.

from environs import Env

from accelbyte_grpc_plugin.utils import create_env as _create_env


def create_env(**kwargs) -> Env:
    env = _create_env(**kwargs)

    env("AB_BASE_URL")
    env("AB_CLIENT_ID")
    env("AB_CLIENT_SECRET")
    env("AB_NAMESPACE")

    ds_provider = env("DS_PROVIDER", "DEMO")
    if ds_provider == "GAMELIFT":
        env("AWS_ACCESS_KEY_ID")
        env("AWS_SECRET_ACCESS_KEY")
        env("AWS_REGION", env("GAMELIFT_REGION"))
    elif ds_provider == "GCP":
        env("GCP_SERVICE_ACCOUNT_FILE")
        env("GCP_PROJECT_ID")
        env("GCP_MACHINE_TYPE")
        env("GCP_REPOSITORY")
        env("GCP_NETWORK", "default")
        env.int("GCP_RETRY", 3)
        env.int("GCP_WAIT_GET_IP", 1)
        env.int("GCP_IMAGE_OPEN_PORT", 8080)
    elif ds_provider == "DEMO":
        pass
    else:
        raise NotImplementedError(ds_provider)

    return env
