from fastapi import Request, status
from fastapi.encoders import jsonable_encoder

from src.core.core_app import AuthenticatedAPIRouter
from src.crud.accounts import Accounts
from src.crud.orders import Orders
from src.api.utils import create_response
from src.api.v1.statistics import schema


router = AuthenticatedAPIRouter(
    prefix='/api/v1/statistics',
    tags=['statistics'],
)


@router.get('/balance', response_model=schema.AccountsInfoResponse)
async def get_info(request: Request):
    account_login = await request.app.user.get_account_login()
    if not account_login:
        data = {
            "no account login, fill account login"
        }
        return create_response(data, status_code=status.HTTP_400_BAD_REQUEST)

    info = jsonable_encoder(
        await Accounts(
            db_engine=request.app.db_engine,
            db_meta=request.app.db_meta
        ).get_account_info(int(account_login))
    )
    if info:
        orders = Orders(
            db_engine=request.app.db_engine,
            db_meta=request.app.db_meta
        )

        info["profit"] = await orders.get_profit(int(account_login)),
        info["predict_profit"] = await orders.get_predicted_profit(int(account_login))
    return create_response(info)


# TODO create response model
@router.get('/open_orders', response_model=schema.OpenOrdersResponse)
async def get_statistic(request: Request, limit: int = 20, offset: int = 0):
    account_login = await request.app.user.get_account_login()
    if not account_login:
        data = {
            "no account login, fill account login"
        }
        return create_response(data, status_code=status.HTTP_400_BAD_REQUEST)

    orders = Orders(
        db_engine=request.app.db_engine,
        db_meta=request.app.db_meta
    )
    open_orders, total = await orders.get_orders(
        account_login=int(account_login),
        order_is_closed=False,
        limit=limit,
        offset=offset
    )
    data = {
        "rows": open_orders,
        "total": total
    }
    return create_response(data)


# TODO create response model
@router.get('/profit_stats')
async def get_profit_stats(request: Request):
    account_login = await request.app.user.get_account_login()
    if not account_login:
        data = {
            "no account login, fill account login"
        }
        return create_response(data, status_code=status.HTTP_400_BAD_REQUEST)

    orders = Orders(
        db_engine=request.app.db_engine,
        db_meta=request.app.db_meta
    )

    # FIXME calculate percent profit for init balance if prev date is None
    # initial_balance = await Accounts(
    #         db_engine=request.app.db_engine,
    #         db_meta=request.app.db_meta
    #     ).get_initial_balance(account_login)

    day, dict_day = await orders.prepare_chart(account_login, 'day')
    week, dict_week = await orders.prepare_chart(account_login, 'week')
    month, dict_month = await orders.prepare_chart(account_login, 'month')
    year, dict_year = await orders.prepare_chart(account_login, 'year')

    day_percent = {
        'GBPUSD': (dict_day.get("curr_date", {}).get('GBPUSD', 0)-dict_day.get("prev_date", {}).get('GBPUSD', 0))*100/dict_day.get("prev_date", {}).get('GBPUSD', 1),
        'USDCAD': (dict_day.get("curr_date", {}).get('USDCAD', 0)-dict_day.get("prev_date", {}).get('USDCAD', 0))*100/dict_day.get("prev_date", {}).get('USDCAD', 1),
        'EURGBP': (dict_day.get("curr_date", {}).get('EURGBP', 0)-dict_day.get("prev_date", {}).get('EURGBP', 0))*100/dict_day.get("prev_date", {}).get('EURGBP', 1),
        'CADCHF': (dict_day.get("curr_date", {}).get('CADCHF', 0)-dict_day.get("prev_date", {}).get('CADCHF', 0))*100/dict_day.get("prev_date", {}).get('CADCHF', 1),
        'NZDUSD': (dict_day.get("curr_date", {}).get('NZDUSD', 0)-dict_day.get("prev_date", {}).get('NZDUSD', 0))*100/dict_day.get("prev_date", {}).get('NZDUSD', 1),
        'AUDCHF': (dict_day.get("curr_date", {}).get('AUDCHF', 0)-dict_day.get("prev_date", {}).get('AUDCHF', 0))*100/dict_day.get("prev_date", {}).get('AUDCHF', 1),
        'NZDCAD': (dict_day.get("curr_date", {}).get('NZDCAD', 0)-dict_day.get("prev_date", {}).get('NZDCAD', 0))*100/dict_day.get("prev_date", {}).get('NZDCAD', 1),
        'AUDUSD': (dict_day.get("curr_date", {}).get('AUDUSD', 0)-dict_day.get("prev_date", {}).get('AUDUSD', 0))*100/dict_day.get("prev_date", {}).get('AUDUSD', 1),
        'AUDCAD': (dict_day.get("curr_date", {}).get('AUDCAD', 0)-dict_day.get("prev_date", {}).get('AUDCAD', 0))*100/dict_day.get("prev_date", {}).get('AUDCAD', 1),
        'GBPCAD': (dict_day.get("curr_date", {}).get('GBPCAD', 0)-dict_day.get("prev_date", {}).get('GBPCAD', 0))*100/dict_day.get("prev_date", {}).get('GBPCAD', 1),
        'EURJPY': (dict_day.get("curr_date", {}).get('EURJPY', 0)-dict_day.get("prev_date", {}).get('EURJPY', 0))*100/dict_day.get("prev_date", {}).get('EURJPY', 1),
        'AUDJPY': (dict_day.get("curr_date", {}).get('AUDJPY', 0)-dict_day.get("prev_date", {}).get('AUDJPY', 0))*100/dict_day.get("prev_date", {}).get('AUDJPY', 1),
    }
    week_percent = {
        'GBPUSD': (dict_week.get("curr_date", {}).get('GBPUSD', 0)-dict_week.get("prev_date", {}).get('GBPUSD', 0))*100/dict_week.get("prev_date", {}).get('GBPUSD', 1),
        'USDCAD': (dict_week.get("curr_date", {}).get('USDCAD', 0)-dict_week.get("prev_date", {}).get('USDCAD', 0))*100/dict_week.get("prev_date", {}).get('USDCAD', 1),
        'EURGBP': (dict_week.get("curr_date", {}).get('EURGBP', 0)-dict_week.get("prev_date", {}).get('EURGBP', 0))*100/dict_week.get("prev_date", {}).get('EURGBP', 1),
        'CADCHF': (dict_week.get("curr_date", {}).get('CADCHF', 0)-dict_week.get("prev_date", {}).get('CADCHF', 0))*100/dict_week.get("prev_date", {}).get('CADCHF', 1),
        'NZDUSD': (dict_week.get("curr_date", {}).get('NZDUSD', 0)-dict_week.get("prev_date", {}).get('NZDUSD', 0))*100/dict_week.get("prev_date", {}).get('NZDUSD', 1),
        'AUDCHF': (dict_week.get("curr_date", {}).get('AUDCHF', 0)-dict_week.get("prev_date", {}).get('AUDCHF', 0))*100/dict_week.get("prev_date", {}).get('AUDCHF', 1),
        'NZDCAD': (dict_week.get("curr_date", {}).get('NZDCAD', 0)-dict_week.get("prev_date", {}).get('NZDCAD', 0))*100/dict_week.get("prev_date", {}).get('NZDCAD', 1),
        'AUDUSD': (dict_week.get("curr_date", {}).get('AUDUSD', 0)-dict_week.get("prev_date", {}).get('AUDUSD', 0))*100/dict_week.get("prev_date", {}).get('AUDUSD', 1),
        'AUDCAD': (dict_week.get("curr_date", {}).get('AUDCAD', 0)-dict_week.get("prev_date", {}).get('AUDCAD', 0))*100/dict_week.get("prev_date", {}).get('AUDCAD', 1),
        'GBPCAD': (dict_week.get("curr_date", {}).get('GBPCAD', 0)-dict_week.get("prev_date", {}).get('GBPCAD', 0))*100/dict_week.get("prev_date", {}).get('GBPCAD', 1),
        'EURJPY': (dict_week.get("curr_date", {}).get('EURJPY', 0)-dict_week.get("prev_date", {}).get('EURJPY', 0))*100/dict_week.get("prev_date", {}).get('EURJPY', 1),
        'AUDJPY': (dict_week.get("curr_date", {}).get('AUDJPY', 0)-dict_week.get("prev_date", {}).get('AUDJPY', 0))*100/dict_week.get("prev_date", {}).get('AUDJPY', 1),
    }
    month_percent = {
        'GBPUSD': (dict_month.get("curr_date", {}).get('GBPUSD', 0)-dict_month.get("prev_date", {}).get('GBPUSD', 0))*100/dict_month.get("prev_date", {}).get('GBPUSD', 1),
        'USDCAD': (dict_month.get("curr_date", {}).get('USDCAD', 0)-dict_month.get("prev_date", {}).get('USDCAD', 0))*100/dict_month.get("prev_date", {}).get('USDCAD', 1),
        'EURGBP': (dict_month.get("curr_date", {}).get('EURGBP', 0)-dict_month.get("prev_date", {}).get('EURGBP', 0))*100/dict_month.get("prev_date", {}).get('EURGBP', 1),
        'CADCHF': (dict_month.get("curr_date", {}).get('CADCHF', 0)-dict_month.get("prev_date", {}).get('CADCHF', 0))*100/dict_month.get("prev_date", {}).get('CADCHF', 1),
        'NZDUSD': (dict_month.get("curr_date", {}).get('NZDUSD', 0)-dict_month.get("prev_date", {}).get('NZDUSD', 0))*100/dict_month.get("prev_date", {}).get('NZDUSD', 1),
        'AUDCHF': (dict_month.get("curr_date", {}).get('AUDCHF', 0)-dict_month.get("prev_date", {}).get('AUDCHF', 0))*100/dict_month.get("prev_date", {}).get('AUDCHF', 1),
        'NZDCAD': (dict_month.get("curr_date", {}).get('NZDCAD', 0)-dict_month.get("prev_date", {}).get('NZDCAD', 0))*100/dict_month.get("prev_date", {}).get('NZDCAD', 1),
        'AUDUSD': (dict_month.get("curr_date", {}).get('AUDUSD', 0)-dict_month.get("prev_date", {}).get('AUDUSD', 0))*100/dict_month.get("prev_date", {}).get('AUDUSD', 1),
        'AUDCAD': (dict_month.get("curr_date", {}).get('AUDCAD', 0)-dict_month.get("prev_date", {}).get('AUDCAD', 0))*100/dict_month.get("prev_date", {}).get('AUDCAD', 1),
        'GBPCAD': (dict_month.get("curr_date", {}).get('GBPCAD', 0)-dict_month.get("prev_date", {}).get('GBPCAD', 0))*100/dict_month.get("prev_date", {}).get('GBPCAD', 1),
        'EURJPY': (dict_month.get("curr_date", {}).get('EURJPY', 0)-dict_month.get("prev_date", {}).get('EURJPY', 0))*100/dict_month.get("prev_date", {}).get('EURJPY', 1),
        'AUDJPY': (dict_month.get("curr_date", {}).get('AUDJPY', 0)-dict_month.get("prev_date", {}).get('AUDJPY', 0))*100/dict_month.get("prev_date", {}).get('AUDJPY', 1),
    }
    year_percent = {
        'GBPUSD': (dict_year.get("curr_date", {}).get('GBPUSD', 0)-dict_year.get("prev_date", {}).get('GBPUSD', 0))*100/dict_year.get("prev_date", {}).get('GBPUSD', 1),
        'USDCAD': (dict_year.get("curr_date", {}).get('USDCAD', 0)-dict_year.get("prev_date", {}).get('USDCAD', 0))*100/dict_year.get("prev_date", {}).get('USDCAD', 1),
        'EURGBP': (dict_year.get("curr_date", {}).get('EURGBP', 0)-dict_year.get("prev_date", {}).get('EURGBP', 0))*100/dict_year.get("prev_date", {}).get('EURGBP', 1),
        'CADCHF': (dict_year.get("curr_date", {}).get('CADCHF', 0)-dict_year.get("prev_date", {}).get('CADCHF', 0))*100/dict_year.get("prev_date", {}).get('CADCHF', 1),
        'NZDUSD': (dict_year.get("curr_date", {}).get('NZDUSD', 0)-dict_year.get("prev_date", {}).get('NZDUSD', 0))*100/dict_year.get("prev_date", {}).get('NZDUSD', 1),
        'AUDCHF': (dict_year.get("curr_date", {}).get('AUDCHF', 0)-dict_year.get("prev_date", {}).get('AUDCHF', 0))*100/dict_year.get("prev_date", {}).get('AUDCHF', 1),
        'NZDCAD': (dict_year.get("curr_date", {}).get('NZDCAD', 0)-dict_year.get("prev_date", {}).get('NZDCAD', 0))*100/dict_year.get("prev_date", {}).get('NZDCAD', 1),
        'AUDUSD': (dict_year.get("curr_date", {}).get('AUDUSD', 0)-dict_year.get("prev_date", {}).get('AUDUSD', 0))*100/dict_year.get("prev_date", {}).get('AUDUSD', 1),
        'AUDCAD': (dict_year.get("curr_date", {}).get('AUDCAD', 0)-dict_year.get("prev_date", {}).get('AUDCAD', 0))*100/dict_year.get("prev_date", {}).get('AUDCAD', 1),
        'GBPCAD': (dict_year.get("curr_date", {}).get('GBPCAD', 0)-dict_year.get("prev_date", {}).get('GBPCAD', 0))*100/dict_year.get("prev_date", {}).get('GBPCAD', 1),
        'EURJPY': (dict_year.get("curr_date", {}).get('EURJPY', 0)-dict_year.get("prev_date", {}).get('EURJPY', 0))*100/dict_year.get("prev_date", {}).get('EURJPY', 1),
        'AUDJPY': (dict_year.get("curr_date", {}).get('AUDJPY', 0)-dict_year.get("prev_date", {}).get('AUDJPY', 0))*100/dict_year.get("prev_date", {}).get('AUDJPY', 1),
    }
    charts = {
        "absolut_profit": {
            "day": day,
            "week": week,
            "month": month,
            "year": year
        },
        "percent_profit": {
            "day": day_percent,
            "week": week_percent,
            "month": month_percent,
            "year": year_percent
        }
    }
    return create_response(charts)
