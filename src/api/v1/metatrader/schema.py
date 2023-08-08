from typing import Optional

from pydantic import BaseModel


class MetatraderStartRequest(BaseModel):
    password: str
    server: Optional[str] = "RoboForex-ECN"


class MetatraderStatusResponse(BaseModel):
    is_deployment_exist: bool
    is_pods_start: bool
    is_stratagy_start: bool
    is_dry_run_on: bool
