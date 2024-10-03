# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.

import random
import string
import time
from argparse import ArgumentParser
from typing import Any, Optional, Tuple

import environs

import accelbyte_py_sdk.api.session as session_service
import accelbyte_py_sdk.api.session.models as session_models
from accelbyte_py_sdk.core import (
    AccelByteSDK,
    DictConfigRepository,
    EnvironmentConfigRepository,
    InMemoryTokenRepository,
    RequestsHttpClient,
    generate_id,
    initialize,
)
from accelbyte_py_sdk.services import auth as auth_service


def generate_password(length: int) -> str:
    strings = [
        string.ascii_lowercase,
        string.ascii_uppercase,
        string.digits,
        "!@#$%^&*()_+-=",
    ]

    si = 0
    result = ""
    for _ in range(length):
        result += random.choice(strings[si])
        si += 1
        if si == len(strings):
            si = 0

    return result


def generate_user(
        country: str = "US",
        date_of_birth: str = "1990-01-01",
        email_domain: str = "test.com",
        user_prefix: str = "python_sdk_",
        namespace: Optional[str] = None,
        sdk: Optional[AccelByteSDK] = None,
) -> Tuple[Optional[Tuple[str, str, str]], Any]:
    import accelbyte_py_sdk.api.iam as iam_service
    import accelbyte_py_sdk.api.iam.models as iam_models
    from accelbyte_py_sdk.core import generate_id

    username = f"{user_prefix}{generate_id(8)}"
    password = generate_password(16)
    email_address = f"{username}@{email_domain}"

    result, error = iam_service.public_create_user_v4(
        body=iam_models.AccountCreateUserRequestV4.create_from_dict(
            {
                "authType": "EMAILPASSWD",
                "country": country,
                "emailAddress": email_address,
                "username": username,
                "password": password,
                # optional
                "dateOfBirth": date_of_birth,
            }
        ),
        namespace=namespace,
        sdk=sdk,
    )
    if error:
        return None, error

    if not (user_id := getattr(result, "user_id", None)):
        return None, "userId not found"

    return (username, password, user_id), None


def create_user_sdk(
    username: str, password: str, existing_sdk: Optional[AccelByteSDK] = None, **kwargs
) -> Tuple[Optional[AccelByteSDK], Any]:
    from accelbyte_py_sdk.services.auth import login_user

    sdk = AccelByteSDK()
    sdk.initialize(
        options={
            "config": existing_sdk.get_config_repository()
            if existing_sdk is not None
            else EnvironmentConfigRepository(),
            "token": InMemoryTokenRepository(),
        }
    )

    result, error = login_user(
        username=username,
        password=password,
        sdk=sdk,
        **kwargs,
    )
    if error:
        return None, error

    return sdk, None


def delete_user(
    user_id: str,
    namespace: Optional[str] = None,
    sdk: Optional[AccelByteSDK] = None,
):
    import accelbyte_py_sdk.api.iam as iam_service

    _, _ = iam_service.admin_delete_user_information_v3(
        user_id=user_id,
        namespace=namespace,
        sdk=sdk,
    )


def main(app_name: Optional[str] = None, grpc_target: Optional[str] = None, **kwargs) -> None:
    env = environs.Env(
        eager=kwargs.get("env_eager", True),
        expand_vars=kwargs.get("env_expand_vars", False),
    )
    env.read_env(
        path=kwargs.get("env_path", None),
        recurse=kwargs.get("env_recurse", True),
        verbose=kwargs.get("env_verbose", False),
        override=kwargs.get("env_override", False),
    )

    env("AB_BASE_URL")
    env("AB_CLIENT_ID")
    env("AB_CLIENT_SECRET")
    namespace = env("AB_NAMESPACE")

    if not app_name:
        app_name = env("APP_NAME", "")
    if not grpc_target:
        grpc_target = env("GRPC_TARGET", "")

    env.float("DS_WAIT_INTERVAL", 0.5)
    env.float("DS_CHECK_COUNT", 10)

    config = DictConfigRepository(dict(env.dump()))
    token = InMemoryTokenRepository()
    http = RequestsHttpClient()
    initialize(
        options={
            "config": config,
            "token": token,
            "http": http,
        }
    )

    _, error = auth_service.login_client()
    if error:
        raise Exception(str(error))

    body_name = f"python-extend-test-{generate_id(8)}"
    body = session_models.ApimodelsCreateConfigurationTemplateRequest.create(
        client_version="test",
        deployment="test",
        persistent=False,
        text_chat=False,
        name=body_name,
        min_players=1,
        max_players=2,
        max_active_sessions=-1,
        joinability="OPEN",
        invite_timeout=60,
        inactive_timeout=60,
        auto_join=True,
        type_="DS",
        ds_source="custom",
        ds_manual_set_ready=False,
        requested_regions=["us-west-2"],
    )

    if app_name:
        body.app_name = app_name
    elif grpc_target:
        body.custom_urlgrpc = grpc_target
    else:
        raise ValueError("Missing one of --app_name and --grpc_target")

    try:
        print("Creating Session Configuration Template...")
        cct_result, error = session_service.admin_create_configuration_template_v1(
            body=body,
        )
        if error:
            exit(f"Unable to Create Session Configuration Template: {error}")
        print("  [ok]")

        user_id = ""
        try:
            print("Creating User...")
            generate_user_result, error = generate_user()
            if error:
                exit(f"Unable to Create User: {error}")

            username, password, user_id = generate_user_result
            user_sdk, error = create_user_sdk(
                username=username,
                password=password,
            )
            if error:
                exit(f"Unable to Create User SDK: {error}")

            print("  [ok]")

            session_id = ""
            try:
                print("Creating Game Session...")
                cgs_result, error = session_service.create_game_session(
                    body=session_models.ApimodelsCreateGameSessionRequest.create_from_dict(
                        {"configurationName": body_name}
                    ),
                    sdk=user_sdk,
                )
                if error:
                    exit(f"Unable to Create Game Session: {error}")

                session_id = cgs_result.id_
                print("  [ok]")

                print("Waiting for Game Session...")
                is_ds_available: bool = False
                ds_checks: int = 0
                max_ds_checks: int = env.int("DS_CHECK_COUNT", 10)
                check_interval: float = env.float("DS_WAIT_INTERVAL", 0.5)
                while True:
                    session_data, error = session_service.get_game_session(
                        session_id=session_id,
                        sdk=user_sdk,
                    )

                    if (
                        not error
                        and session_data
                        and isinstance(session_data, session_models.ApimodelsGameSessionResponse)
                    ):
                        if (
                            session_data.ds_information
                            and isinstance(session_data.ds_information, session_models.ApimodelsDSInformationResponse)
                        ):
                            if (
                                session_data.ds_information.status_v2 == "AVAILABLE"
                                and session_data.ds_information.server
                            ):
                                is_ds_available = True
                                print(f"  DS is AVAILABLE\n"
                                      f"  {session_data.ds_information.server.ip}:"
                                      f"{session_data.ds_information.server.port}\n"
                                      f"  [found]")
                                break

                    ds_checks += 1
                    if ds_checks == max_ds_checks:
                        break

                    time.sleep(check_interval)

            finally:
                if session_id:
                    print("Deleting Game Session...")
                    _, _ = session_service.delete_game_session(
                        session_id=session_id,
                        sdk=user_sdk,
                    )
                    print("  [ok]")
        finally:
            if user_id:
                print("Deleting User...")
                delete_user(user_id=user_id)
                print("  [ok]")
    finally:
        print("Deleting Session Configuration Template...")
        _, _ = session_service.admin_delete_configuration_template_v1(name=body_name)
        print("  [ok]")


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        "-a",
        "--app_name",
        default=None,
        required=False,
        help="[A]pp Name",
    )
    parser.add_argument(
        "-g",
        "--grpc_target",
        default=None,
        required=False,
        help="[G]rpc Target",
    )
    result = vars(parser.parse_args())
    return result


if __name__ == "__main__":
    main(**parse_args())
