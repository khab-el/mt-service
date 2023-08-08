from typing import List, Optional, Dict

from pydantic import BaseModel


class ApiError(BaseModel):
    message: str


class ApiErrorResponse(BaseModel):
    answer: Optional[Dict] = None
    success: bool = False
    errors: List[ApiError]
