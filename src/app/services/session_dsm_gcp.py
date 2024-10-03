# Copyright (c) 2024 AccelByte Inc. All Rights Reserved.
# This is licensed software from AccelByte Inc, for limitations
# and restrictions contact your company contract manager.
import asyncio
import json
import random

from logging import Logger
from typing import Any, Dict, List, Optional, Tuple

from google.api_core.extended_operation import ExtendedOperation
from google.cloud import compute_v1
from google.oauth2 import service_account
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


def wait_for_extended_operation(
    operation: ExtendedOperation,
    verbose_name: str = "operation",
    timeout: int = 300,
    logger: Optional[Logger] = None,
) -> Any:
    """
    Waits for the extended (long-running) operation to complete.

    If the operation is successful, it will return its result.
    If the operation ends with an error, an exception will be raised.
    If there were any warnings during the execution of the operation
    they will be printed to sys.stderr.

    Args:
        operation: a long-running operation you want to wait on.
        verbose_name: (optional) a more verbose name of the operation,
            used only during error and warning reporting.
        timeout: how long (in seconds) to wait for operation to finish.
            If None, wait indefinitely.
        logger: (optional) the logger to log errors and warnings to.

    Returns:
        Whatever the operation.result() returns.

    Raises:
        This method will raise the exception received from `operation.exception()`
        or RuntimeError if there is no exception set, but there is an `error_code`
        set for the `operation`.

        In case of an operation taking longer than `timeout` seconds to complete,
        a `concurrent.futures.TimeoutError` will be raised.
    """
    result = operation.result(timeout=timeout)

    if operation.error_code:
        if logger:
            logger.error(
                f"Error during {verbose_name}: [Code: {operation.error_code}]: {operation.error_message}\n"
                f"Operation ID: {operation.name}"
            )
        raise operation.exception() or RuntimeError(operation.error_message)

    if operation.warnings:
        if logger:
            logger.warning(
                f"Warnings during {verbose_name}:\n - "
                + "\n - ".join(
                    f"{warning.code}: {warning.message}"
                    for warning in operation.warnings
                )
            )

    return result


class AsyncSessionDsmGcpService(SessionDsmServicer):
    full_name: str = DESCRIPTOR.services_by_name["SessionDsm"].full_name

    aws_to_gcp_region_map: Dict[str, str] = {
        "us-east-1": "us-east1",
        "us-east-2": "us-east4",
        "us-west-1": "us-west1",
        "us-west-2": "us-west2",
        "ca-central-1": "northamerica-northeast1",
        "sa-east-1": "southamerica-east1",
        "eu-central-1": "europe-west3",
        "eu-west-1": "europe-west1",
        "eu-west-2": "europe-west2",
        "eu-west-3": "europe-west9",
        "eu-north-1": "europe-north1",
        "me-south-1": "me-west1",
        "af-south-1": "africa-north1",
        "ap-east-1": "asia-east2",
        "ap-south-1": "asia-south1",
        "ap-northeast-3": "asia-northeast2",
        "ap-northeast-2": "asia-northeast3",
        "ap-southeast-1": "asia-southeast1",
        "ap-southeast-2": "australia-southeast1",
        "ap-northeast-1": "asia-northeast1",
    }

    gcp_zones_map: Dict[str, List[str]] = {
        "us-east1": ["us-east1-b", "us-east1-c", "us-east1-d"],
        "us-east4": ["us-east4-a", "us-east4-b", "us-east4-c"],
        "us-west1": ["us-west1-a", "us-west1-b", "us-west1-c"],
        "us-west2": ["us-west2-a", "us-west2-b", "us-west2-c"],
        "northamerica-northeast1": [
            "northamerica-northeast1-a",
            "northamerica-northeast1-b",
            "northamerica-northeast1-c",
        ],
        "southamerica-east1": [
            "southamerica-east1-a",
            "southamerica-east1-b",
            "southamerica-east1-c",
        ],
        "europe-west3": ["europe-west3-a", "europe-west3-b", "europe-west3-c"],
        "europe-west1": ["europe-west1-b", "europe-west1-c", "europe-west1-d"],
        "europe-west2": ["europe-west2-a", "europe-west2-b", "europe-west2-c"],
        "europe-west9": ["europe-west9-a", "europe-west9-b", "europe-west9-c"],
        "europe-north1": ["europe-north1-a", "europe-north1-b", "europe-north1-c"],
        "me-west1": ["me-west1-a", "me-west1-b", "me-west1-c"],
        "africa-north1": ["africa-north1-a", "africa-north1-b", "africa-north1-c"],
        "asia-east2": ["asia-east2-a", "asia-east2-b", "asia-east2-c"],
        "asia-south1": ["asia-south1-a", "asia-south1-b", "asia-south1-c"],
        "asia-northeast2": [
            "asia-northeast2-a",
            "asia-northeast2-b",
            "asia-northeast2-c",
        ],
        "asia-northeast3": [
            "asia-northeast3-a",
            "asia-northeast3-b",
            "asia-northeast3-c",
        ],
        "asia-southeast1": [
            "asia-southeast1-a",
            "asia-southeast1-b",
            "asia-southeast1-c",
        ],
        "australia-southeast1": [
            "australia-southeast1-a",
            "australia-southeast1-b",
            "australia-southeast1-c",
        ],
        "asia-northeast1": [
            "asia-northeast1-a",
            "asia-northeast1-b",
            "asia-northeast1-c",
        ],
    }

    def __init__(
        self,
        service_account_file: str,
        project_id: str,
        machine_type: str,
        network_name: str,
        repository_name: str,
        image_open_port: int,
        max_retries: int = 3,
        retry_interval: float = 5,
        logger: Optional[Logger] = None,
    ) -> None:
        self.service_account_file = service_account_file
        self.project_id = project_id
        self.machine_type = machine_type
        self.network_name = network_name

        self.repository_name = repository_name
        self.image_open_port = image_open_port

        self.max_retries = max_retries
        self.retry_interval = retry_interval

        self.logger = logger

        self.credentials = service_account.Credentials.from_service_account_file(
            filename=service_account_file,
        )
        self.instances_client = compute_v1.InstancesClient(credentials=self.credentials)

    async def delete_instance(self, instance_name: str, zone: str) -> Tuple[bool, str]:
        di_request = compute_v1.DeleteInstanceRequest(
            project=self.project_id,
            zone=zone,
            instance=instance_name,
        )

        di_operation = self.instances_client.delete(
            request=di_request,
        )

        success: bool = True
        message: str = ""
        try:
            di_response = wait_for_extended_operation(
                operation=di_operation,
                verbose_name="DeleteInstanceRequest",
                logger=self.logger,
            )

            success: bool = not di_operation.error_message
            message: str = di_operation.error_message
        except Exception as exception:
            success = False
            message = str(exception)

        return success, message

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

        # translate
        if selected_region not in self.aws_to_gcp_region_map:
            code: StatusCode = StatusCode.INVALID_ARGUMENT
            details: str = f"Unknown AWS Region: {selected_region}"
            await context.abort(code=code, details=details)

        gcp_region = self.aws_to_gcp_region_map[selected_region]

        if gcp_region not in self.gcp_zones_map:
            code: StatusCode = StatusCode.INVALID_ARGUMENT
            details: str = f"Unknown GCP Region: {gcp_region}"
            await context.abort(code=code, details=details)

        gcp_zones = self.gcp_zones_map[gcp_region]
        gcp_zone = random.choice(gcp_zones)

        try:
            instance_name: str = f"{request.namespace}-{request.session_id}"

            machine_type = self.machine_type

            if "{zone}" in machine_type:
                machine_type = machine_type.replace("{zone}", gcp_zone)

            instance_resource = compute_v1.Instance(
                name=instance_name,
                machine_type=machine_type,
                shielded_instance_config=compute_v1.ShieldedInstanceConfig(
                    enable_integrity_monitoring=True,
                    enable_secure_boot=True,
                    enable_vtpm=True,
                ),
                reservation_affinity=compute_v1.ReservationAffinity(
                    consume_reservation_type="ANY_RESERVATION",
                ),
                confidential_instance_config=compute_v1.ConfidentialInstanceConfig(
                    enable_confidential_compute=False,
                ),
                tags=compute_v1.Tags(
                    items=[
                        "http-server",
                        "https-server",
                    ],
                ),
                metadata=compute_v1.Metadata(
                    items=[
                        compute_v1.Items(
                            key="gce-container-declaration",
                            value=(
                                f"spec:\n"
                                f"  containers:\n"
                                f"  - name: {instance_name}\n"
                                f"    image: {self.repository_name}/{request.deployment}\n"
                                f"    env:\n"
                                f"    - name: SESSION_ID\n"
                                f"      value: {instance_name}\n"
                                f"    securityContext:\n"
                                f"      privileged: true\n"
                                f"    stdin: true\n"
                                f"    tty: true\n"
                                f"  restartPolicy: Never\n"
                                f"# This container declaration format is not public API and may change without notice.\n"
                                f"# Please use gcloud command-line tool or Google Cloud Console to run Containers on\n"
                                f"# Google Compute Engine."
                            ),
                        )
                    ],
                ),
                disks=[
                    compute_v1.AttachedDisk(
                        auto_delete=True,
                        boot=True,
                        device_name=f"{instance_name}-disk",
                        initialize_params=compute_v1.AttachedDiskInitializeParams(
                            disk_size_gb=10,
                            disk_type=f"projects/{self.project_id}/zones/{gcp_zone}/diskTypes/pd-balanced",
                            source_image="projects/cos-cloud/global/images/cos-stable-113-18244-85-5",
                        ),
                        mode="READ_WRITE",
                        type="PERSISTENT",
                    ),
                ],
                network_interfaces=[
                    compute_v1.NetworkInterface(
                        stack_type="IPV4_ONLY",
                        subnetwork=f"projects/{self.project_id}/regions/{gcp_region}/subnetworks/{self.network_name}",
                        access_configs=[
                            compute_v1.AccessConfig(
                                name="External NAT",
                                network_tier="PREMIUM",
                            )
                        ],
                    ),
                ],
            )

            ii_request = compute_v1.InsertInstanceRequest(
                project=self.project_id,
                zone=gcp_zone,
                instance_resource=instance_resource,
            )

            ii_operation = self.instances_client.insert(
                request=ii_request,
            )

            ii_response = wait_for_extended_operation(
                operation=ii_operation,
                verbose_name="InsertInstanceRequest",
                logger=self.logger,
            )

            gi_request = compute_v1.GetInstanceRequest(
                project=self.project_id,
                zone=gcp_zone,
                instance=instance_name,
            )

            instance_ready: bool = False
            check_retry: int = 0
            while True:
                gi_response = self.instances_client.get(
                    request=gi_request,
                )

                if gi_response.status == "RUNNING":
                    instance_ready = True
                    break

                check_retry += 1
                if check_retry == self.max_retries:
                    break
                await asyncio.sleep(self.retry_interval)

            if instance_ready:
                external_ip: str = ""
                for network_interface in gi_response.network_interfaces:
                    if len(network_interface.access_configs) > 0:
                        external_ip = network_interface.access_configs[0].nat_i_p
                        break

                response.client_version = request.client_version
                response.created_region = gcp_zone
                response.deployment = request.deployment
                response.game_mode = request.game_mode
                response.namespace = request.namespace
                response.port = self.image_open_port
                response.region = selected_region
                response.server_id = instance_name
                response.session_data = request.session_data
                response.session_id = request.session_id
                response.source = "GCP"
                response.status = "READY"

                response.ip = external_ip

                self.log_payload(
                    f"{self.CreateGameSession.__name__} response: %s", response
                )

                # success

            else:
                # clean-up

                delete_success, _ = await self.delete_instance(
                    instance_name=instance_name,
                    zone=gcp_zone,
                )

                if delete_success:
                    raise Exception("Instance creation process failed.")
                else:
                    raise Exception(
                        "Instance creation process isn't finish and failed to delete it."
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

        instance_name = f"{request.namespace}-{request.session_id}"

        success, message = await self.delete_instance(
            instance_name=instance_name,
            zone=request.zone,
        )

        if not success:
            code: StatusCode = StatusCode.INTERNAL
            details: str = f"TerminateGameSession Exception: Could not delete instance: {instance_name}"
            await context.abort(code=code, details=details)

        response = ResponseTerminateGameSession()

        response.namespace = request.namespace
        response.reason = message
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
    "AsyncSessionDsmGcpService",
]
