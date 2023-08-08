from fastapi import Request

from src.core.core_app import AuthenticatedAPIRouter
from src.api.utils import create_response
from src.settings import settings
from src.modules.s3_response import S3Stream
from src.api.v1.strategy import schema
from src.api.v1.strategy.utils import stratagy_manager, send_strategy_to_client

router = AuthenticatedAPIRouter(
    prefix="/api/v1/strategy",
    tags=["strategy"],
)


@router.get("/download")
async def download_compiled_strat(request: Request):
    object_file_name = "compiled-strats/" + request.app.user.params.sub
    s3_session = request.app.boto_client
    return S3Stream(
        content=None,
        bucket=settings.BUCKET_NAME,
        key=object_file_name,
        s3_session=s3_session,
        s3_end_point_url=settings.AWS_BUCKET_ENDPOINT,
        media_type="application/binary",
    )


@router.post(
    "/",
    response_model=schema.SendStratagyResponse,
    description=f"avaliable command {schema.Command.list()}"
)
async def command_manager(request: Request, data: schema.StratagyRequest):
    sub = request.app.user.params.sub
    name = request.app.user.params.name
    user_email = request.app.user.params.email
    if data.command == "mail":
        boto_client = request.app.boto_client
        mail_client = request.app.mail_client
        await send_strategy_to_client(boto_client, mail_client, sub, name, user_email)
        msg = {"status": "stratagy send to email - {user_email}"}
        status_code = 200
    else:
        threads = request.app.threads
        msg, status_code = await stratagy_manager(threads, data.command, sub)

    return create_response(msg, status_code=status_code)
