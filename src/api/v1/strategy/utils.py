from uuid import UUID

from aioboto3 import Session
from aiosmtplib import SMTP

from src.modules.thread_client import ThreadClient
from src.modules.metatrader import request_mt
from src.settings import settings
from src.constans import EMAIL_STRATEGY_TEMPLATE
from src.modules.email import send


async def send_strategy_to_client(boto_client: Session, mail_client: SMTP, sub: UUID, user_name: str, email: str):
    object_file_name = "compiled-strats/" + str(sub)
    templated_email = EMAIL_STRATEGY_TEMPLATE.replace('USER_NAME', user_name)
    async with boto_client.client(
        service_name="s3", endpoint_url=settings.AWS_BUCKET_ENDPOINT
    ) as s3:
        response_object = await s3.get_object(
            Bucket=settings.BUCKET_NAME, Key=object_file_name
        )
        await send(
            mail_client,
            email=email,
            email_subject="trading strategy",
            email_message=templated_email,
            email_message_type="html",
            attach=response_object,
        )


async def stratagy_manager(threads: ThreadClient, command: str, sub: UUID):
    status = True
    for port in range(1111, 1123):
        service_name = f"{settings.k8s_name}-{sub}.{settings.namespace}.svc.cluster.local:{port}"
        message = await threads.exec(
            request_mt, service_name, command.upper()
        )

        if message["status"] == 200:
            status = status and True
        else:
            status = status and False
            break

    msg = {"stratagy": command} if status else "unknown command or error"
    status_code = 200 if status else 401

    return msg, status_code
