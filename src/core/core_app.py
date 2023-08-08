from logging import Logger

from aiosmtplib import SMTP
from aioboto3 import Session
from aiopg.sa import Engine
from fastapi import FastAPI, APIRouter, Depends
from sqlalchemy import MetaData
from zmq import Context

from src.crud.users import User
from src.modules.thread_client import ThreadClient
from src.auth.auth import authenticate, admin_access


class AppFastAPI(FastAPI):
    """
    FastApi class for app
    """

    db_engine: Engine
    context: Context
    boto_client: Session
    mail_client: SMTP
    db_meta: MetaData
    logger: Logger
    threads: ThreadClient
    user: User = None


class AuthenticatedAPIRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        dependencies = list(kwargs.pop('dependencies', None) or [])
        dependencies.insert(0, Depends(authenticate))
        kwargs['dependencies'] = dependencies
        super(AuthenticatedAPIRouter, self).__init__(*args, **kwargs)


class AdminAPIRouter(APIRouter):
    def __init__(self, *args, **kwargs):
        dependencies = list(kwargs.pop('dependencies', None) or [])
        dependencies.insert(0, Depends(authenticate))
        dependencies.insert(1, Depends(admin_access))
        kwargs['dependencies'] = dependencies
        super(AdminAPIRouter, self).__init__(*args, **kwargs)
