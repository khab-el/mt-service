from enum import Enum

from pydantic import BaseModel


class Command(str, Enum):
    start = "start"
    stop = "stop"
    dryon = "dryon"
    dryoff = "dryoff"
    mail = "mail"

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class StratagyRequest(BaseModel):
    command: Command


class SendStratagyResponse(BaseModel):
    status: str
