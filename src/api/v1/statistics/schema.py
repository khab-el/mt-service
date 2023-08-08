from typing import List
from datetime import datetime

from pydantic import BaseModel


class AccountsInfoResponse(BaseModel):
    account_login: int
    initial_balance: float
    minimal_balance: float
    account_balance: float
    account_equity: float
    account_profit: float
    account_margin: float
    account_margin_free: float
    account_margin_level: float
    max_peak: float
    next_min_peak: float
    abs_drawdown: float
    max_drawdown: float
    max_drawdown_perc: float
    profit: dict
    predict_profit: dict


class Order(BaseModel):
    account_login: int
    initial_balance: float
    minimal_balance: float
    account_balance: float
    account_equity: float
    account_profit: float
    account_margin: float
    account_margin_free: float
    account_margin_level: float
    max_peak: float
    next_min_peak: float
    abs_drawdown: float
    max_drawdown: float
    max_drawdown_perc: float
    server_time: datetime


class OpenOrdersResponse(BaseModel):
    rows: List[Order]
    total: int


class ProfitResponse(BaseModel):
    absolut_profit: dict
    percent_profit: dict
