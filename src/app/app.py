import time
import asyncio

from aioboto3 import Session
from aiosmtplib import SMTP
from aiopg.sa import create_engine
from fastapi import Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from src.api import v1
from src.api import base_schema
from src.api.health_check import srv_router
from src.core.core_app import AppFastAPI
from src.core.logger import get_logger
from src.database.pg import reflect_meta
from src.modules.thread_client import ThreadClient
from src.metrics import metrics
from src.settings import settings
from src.worker.worker import init_worker


def init_app(api=False, consume=False) -> AppFastAPI:
    app = AppFastAPI(
        title='Trading-Bot Backend Service.',
        description='Trading-Bot. Backend Service.',
        version=settings.GIT_TAG_NAME or settings.GIT_COMMIT_ID or "0.0.0",
        docs_url="/api/docs" if settings.ENV != "prod" else None,
        redoc_url="/api/redoc" if settings.ENV != "prod" else None,
        openapi_url="/api/openapi.json" if settings.ENV != "prod" else None,
        responses={
            500: {"model": base_schema.ApiErrorResponse},
        }
    )

    @app.on_event("startup")
    async def startup_event():
        app.db_engine = await create_engine(
            dsn=settings.DATABASE_URL,
            maxsize=settings.DB_MAX_CONNECTIONS,
            pool_recycle=settings.DC_POOL_RECYCLE,
        )
        app.db_meta = reflect_meta(settings.DATABASE_URL)
        app.threads = ThreadClient(n_workers=settings.N_WORKERS)
        if consume:
            app.logger = get_logger("consume")
            asyncio.create_task(init_worker())
        if api:
            app.boto_client = Session(
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.BUCKET_KEY
            )
            app.mail_client = SMTP(hostname=settings.SMTP_SERVER, port=settings.SMTP_PORT, use_tls=True)
            app.logger = get_logger("api")

    @app.on_event("shutdown")
    async def shutdown() -> None:
        app.db_engine.close()
        await app.db_engine.wait_closed()
        await app.threads.close()

    if api:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @app.middleware("http")
        async def middleware(request: Request, call_next):
            ts_start = time.monotonic()
            method = request.scope["method"]
            path = request.url.path
            metrics.requests.labels(path, method).inc()

            try:
                response = await call_next(request)
                status_code = response.status_code
            except Exception as exc:
                err_msg = str(exc)
                status_code = 500
                if str(exc.__class__) == "<class 'botocore.errorfactory.NoSuchKey'>":
                    err_msg = 'there is no compiled strategy in bucket. compile it before download'
                    status_code = 404

                request.app.logger.exception(f"{method}, {path}, status - {status_code},\n {str(exc)}")

                data = dict(
                    success=False,
                    errors=[{"message": err_msg}]
                )
                response = JSONResponse(data, status_code=status_code)

            elapsed = time.monotonic() - ts_start
            metrics.timings.labels(path, method).observe(elapsed)

            metrics.responses.labels(path, method, status_code).inc()
            return response

        app.include_router(v1.user_router)
        app.include_router(v1.admin_user_router)
        app.include_router(v1.mt_router)
        app.include_router(v1.referal_router)
        app.include_router(v1.strategy_router)
        app.include_router(v1.statistics_router)

    app.include_router(srv_router)

    return app
