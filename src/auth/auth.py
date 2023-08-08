import jwt
from fastapi import Request, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.exceptions import HTTPException

from src.modules.dotdict import Map
from src.settings import settings
from src.crud.users import User


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=settings.KEYCLOAK_URL
)


async def authenticate(
    request: Request,
    token: str = Depends(oauth2_scheme),
):
    decoded_token = Map(jwt.decode(token, verify=False))
    request.app.user = User(
        db_engine=request.app.db_engine,
        db_meta=request.app.db_meta,
        params=decoded_token
    )
    if not await request.app.user.is_exist():
        await request.app.user.add_user()


async def admin_access(request: Request):
    if not request.app.user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
            headers={"WWW-Authenticate": "Bearer"},
        )
