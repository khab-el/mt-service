from uuid import UUID
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, root_validator


class Link(BaseModel):
    id: int
    source: Optional[int]
    target: Optional[int]


class User(BaseModel):
    id: int
    sub: UUID
    account_login: Optional[int]
    name: str
    code: str
    email: str
    is_stratagy_buy: bool
    is_confirm_stratagy: bool
    is_subscription_buy: bool
    is_confirm_subscription: bool
    is_admin: bool


class UserResponse(User):
    referal: List[Link]


class UsersResponse(BaseModel):
    rows: List[User]
    total: int


class UserMailResponse(BaseModel):
    status: str


class Command(str, Enum):
    stratagy = "stratagy"
    subscription = "subscription"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class ConfirmRequest(BaseModel):
    command: Command


class PaymentRequest(BaseModel):
    command: Command
    account_login: Optional[int]

    @root_validator(pre=False)
    def valid_flat_id(cls, values):
        command, account_login = values.get("command"), values.get("account_login")
        if command == "stratagy" and account_login is None:
            raise ValueError("specify account_login for command stratagy")
        return values
