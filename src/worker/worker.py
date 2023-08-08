from celery import Celery
from fastapi.concurrency import run_in_threadpool

from src.modules.kubernetes import metatrader_service
from src.settings import settings


celery = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


@celery.task(name="start_mt_pod")
def start_mt_pod(
    client_id: str,
    login: int,
    password: str,
    server: str
):
    metatrader_service.create_user_services(
        client_id=client_id,
        login=login,
        password=password,
        server=server
    )
    return True


@celery.task(name="compile_task")
def compile_task(data):
    metatrader_service.create_job(**data)
    return True


async def init_worker():
    argv = [
        'worker',
        '-B',
        f'--loglevel={settings.LOG_LEVEL}',
    ]
    await run_in_threadpool(celery.worker_main, argv)
