from fastapi import Request
from fastapi.encoders import jsonable_encoder

from src.core.core_app import AuthenticatedAPIRouter, AdminAPIRouter
from src.api.v1.users import schema
from src.api.utils import create_response
from src.crud.links import Link
from src.modules import email
from src.api.v1.users.utils import run_compile_job

router = AuthenticatedAPIRouter(
    prefix="/api/v1/users",
    tags=["user"],
)


admin_router = AdminAPIRouter(
    prefix="/api/v1/users",
    tags=["user"],
)


@router.get("/self", response_model=schema.UserResponse)
async def get_me(request: Request):
    user = jsonable_encoder(await request.app.user.get_user())
    link = Link(
        db_engine=request.app.db_engine,
        db_meta=request.app.db_meta
    )
    user["referal"] = await link.get_referal_by_user(user["id"])
    return create_response(user)


@router.put("/self/payment", response_model=schema.UserResponse)
async def stratagy_payment(request: Request, data: schema.PaymentRequest):
    f"""Update info about user and create job for compiling stratagy\n
    avaliable command {schema.Command.list()}
    for command stratagy provide account_login
    """
    if data.command == "stratagy":
        user = await request.app.user.update_stratagy_buy(
            account_login=data.account_login
        )
        run_compile_job(
            account_login=data.account_login,
            sub=request.app.user.params.sub
        )
    else:
        user = await request.app.user.update_subscription_buy()

    return create_response(user)


@admin_router.put(
    "/{user_id}/confirmation",
    response_model=schema.UserResponse,
    description=f"avaliable command {schema.Command.list()}"
)
async def confirm_payment(request: Request, user_id: int, data: schema.ConfirmRequest):
    """only for user with role web_admin"""
    if data.command == "stratagy":
        user = await request.app.user.confirm_stratagy_payment(user_id)
    else:
        # TODO update subcription tbl
        user = await request.app.user.confirm_subscription_payment(user_id)

    return create_response(user)


@admin_router.get("/", response_model=schema.UsersResponse)
async def get_users(request: Request, limit: int = 20, offset: int = 0):
    """only for user with role web_admin"""
    user, total = await request.app.user.get_users(limit, offset)
    data = {
        "rows": user,
        "total": total
    }
    return create_response(data)


@router.post("/self/mail", response_model=schema.UsersResponse)
async def send_mail_to_user(request: Request, email_subject: str, email_message: str):
    await email.send(
        request.app.mail_client,
        email=request.app.user.params.email,
        email_subject=email_subject,
        email_message=email_message
    )
    return create_response({"status": f"email sent to {request.app.user.params.email}"})
