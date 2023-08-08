import prometheus_client as pc
from fastapi import APIRouter, HTTPException, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, PlainTextResponse

from src.core.logger import get_logger

logger = get_logger(__name__)


srv_router = APIRouter(
    tags=["helth_check"],
    include_in_schema=False
)


@srv_router.get("/ping")
async def ping(request: Request):
    try:
        async with request.app.db_engine.acquire() as conn:
            res = await conn.execute("SELECT 1;")
            data = {"ok": True, "db": bool(await res.scalar())}
            return JSONResponse(
                content=jsonable_encoder(data), status_code=status.HTTP_200_OK
            )
    except Exception:
        request.app.logger.exception("ping db fail")
        raise HTTPException(status.HTTP_400_BAD_REQUEST, detail="База недоступна")


@srv_router.get("/metrics")
async def metrics():
    return PlainTextResponse(pc.generate_latest())
