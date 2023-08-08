from pydantic import BaseModel


class ReferalByUserResponse(BaseModel):
    id: int
    source: int
    target: int
