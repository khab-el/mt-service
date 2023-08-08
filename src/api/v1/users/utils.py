from uuid import UUID

from src.worker.worker import compile_task
from src.core.logger import get_logger

logger = get_logger("app.utils")


def run_compile_job(account_login: int, sub: UUID):
    data = dict(
        client_id=sub,
        login=account_login,
    )
    task = compile_task.delay(data)
    logger.info(f"create task for compiling stratagy - task_id: {task.id}; user - {sub}")
