from fastapi import Request

from src.core.core_app import AuthenticatedAPIRouter
from src.api.v1.referal import schema
from src.api.utils import create_response
from src.crud.links import Link


router = AuthenticatedAPIRouter(
    prefix='/api/v1/referal',
    tags=['referal'],
)


@router.get('/{source}', response_model=schema.ReferalByUserResponse)
async def get_referal_by_user(request: Request, source: int):
    db_engine = request.app.db_engine
    db_meta = request.app.db_meta
    link = Link(db_engine, db_meta)
    return create_response(await link.get_referal_by_user(source))
