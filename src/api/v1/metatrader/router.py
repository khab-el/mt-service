import asyncio

from fastapi import Request

from src.core.core_app import AuthenticatedAPIRouter
from src.api.utils import create_response
from src.worker.worker import start_mt_pod
from src.modules.kubernetes import metatrader_service
from src.modules.metatrader import request_mt
from src.api.v1.metatrader import schema
from src.settings import settings
from src.modules.metatrader import SocketConnectionError


router = AuthenticatedAPIRouter(
    prefix='/api/v1/metatrader',
    tags=['metatrader'],
)


@router.get('/status', response_model=schema.MetatraderStatusResponse)
async def get_status(request: Request):
    k8s_service_name = f"{settings.k8s_name}-{request.app.user.params.sub}"
    is_deployment_exist = False
    is_pods_start = False
    is_stratagy_start = False
    is_dry_run_on = False

    deployment_check = asyncio.create_task(request.app.threads.exec(metatrader_service.get_deployment, k8s_service_name))

    is_pods_start = True
    is_stratagy_start = True
    is_dry_run_on = True
    tasks = []
    for port in range(1111, 1123):
        k8s_service_host = f'{settings.k8s_name}-{request.app.user.params.sub}.{settings.namespace}.svc.cluster.local:{port}'
        task = asyncio.create_task(
            request.app.threads.exec(
                request_mt,
                k8s_service_host,
                "STATUS"
            )
        )
        tasks.append((task, k8s_service_host))

    for task in tasks:
        try:
            message = await task[0]
        except SocketConnectionError:
            request.app.logger.warning(f'message from pod {task[1]}: pod did not open the port yet')
            is_pods_start = False
            is_stratagy_start = False
            is_dry_run_on = False
            break
#TODO refactor shit above :)

        if message["status"] == 200:
            is_pods_start = is_pods_start and True
            is_stratagy_start = is_stratagy_start and bool(message["is_stratagy_start"])
            is_dry_run_on = is_dry_run_on and bool(message["is_dry_run_on"])
        else:
            request.app.logger.warning(f'message from pod {task[1]}: {message}')
            is_pods_start = False
            is_stratagy_start = False
            is_dry_run_on = False
            break

    try:
        await deployment_check
        is_deployment_exist = True
    except Exception:
        request.app.logger.debug("deployment doesn't exist")

    answer = {
        "is_deployment_exist": is_deployment_exist,
        "is_pods_start": is_pods_start,
        "is_stratagy_start": is_stratagy_start,
        "is_dry_run_on": is_dry_run_on
    }
    return create_response(answer)


@router.post('/start')
async def start_bot(request: Request, data: schema.MetatraderStartRequest):
    user = await request.app.user.get_user()
    task = start_mt_pod.delay(
        client_id=request.app.user.params.sub,
        login=user.account_login,
        password=data.password,
        server=data.server
    )
    answer = {
        "task_id": task.id,
        "status": "pending"
    }
    return create_response(answer, 201)


# TODO response model
@router.post('/stop')
async def stop_bot(request: Request):
    await request.app.threads.exec(metatrader_service.delete_user_services, request.app.user.params.sub)
    return create_response({"bot": "teminating"})
