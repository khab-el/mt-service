from sqlalchemy.sql import select
from aiopg.sa import Engine
from sqlalchemy import MetaData


class Accounts:
    def __init__(self, db_engine: Engine, db_meta: MetaData) -> None:
        self.db_engine = db_engine
        self.db_meta = db_meta
        self.tbl_model = db_meta.tables["accounts"]

    async def get_account_info(self, account_login: int):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(self.tbl_model).where(
                    self.tbl_model.c.account_login == account_login
                )
            )
            res = await async_result.fetchone()
            return res

    async def get_initial_balance(self, account_login: int):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(self.tbl_model.c.initial_balance).where(
                    self.tbl_model.c.account_login == account_login
                )
            )
            return await async_result.scalar()
