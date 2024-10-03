# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.

from environs import Env


def create_env(**kwargs) -> Env:
    env = Env(
        eager=kwargs.get("env_eager", True),
        expand_vars=kwargs.get("env_expand_vars", False),
    )
    env.read_env(
        path=kwargs.get("env_path", None),
        recurse=kwargs.get("env_recurse", True),
        verbose=kwargs.get("env_verbose", False),
        override=kwargs.get("env_override", False),
    )
    return env


__all__ = [
    "create_env",
]
