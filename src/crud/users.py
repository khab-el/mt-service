import secrets
from sqlalchemy.sql import select, func
from aiopg.sa import Engine
from sqlalchemy import MetaData, Table
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.sql.expression import false

from src.modules.dotdict import Map
from src.settings import settings


class User:
    def __init__(self, db_engine: Engine, db_meta: MetaData, params: Map) -> None:
        self.db_engine = db_engine
        self.db_meta = db_meta
        self.tbl_model: Table = db_meta.tables["users"]
        self.params = params
        self.is_admin = True if settings.ADMIN_ROLE in params.get("realm_access", {}).get("roles", {}) else False

    async def is_exist(self):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(self.tbl_model).where(
                    self.tbl_model.c.sub == self.params.sub
                )
            )
            return bool(await async_result.scalar())

    async def get_user_by_ref(self):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(self.tbl_model).where(
                    self.tbl_model.c.code == self.params.ref
                )
            )
            res = await async_result.fetchone()
            if res:
                return res

    async def add_user(self):
        query = (
            self.tbl_model.insert()
            .values(
                sub=self.params.sub,
                code=secrets.token_hex(5).upper(),
                name=self.params.name,
                email=self.params.email,
                is_stratagy_buy=false(),
                is_confirm_stratagy=false(),
                is_subscription_buy=false(),
                is_confirm_subscription=false(),
                is_admin=self.is_admin
            )
            .returning(self.tbl_model)
        )

        async with self.db_engine.acquire() as conn:
            res_insert = await conn.execute(query)
            new_user = await res_insert.fetchone()

        if self.params.ref:
            parent = await self.get_user_by_ref()
            if parent:
                tbl_link = self.db_meta.tables["link"]
                query = (
                    pg_insert(tbl_link)
                    .values(
                        source=parent.id,
                        target=new_user.id
                    )
                )
                async with self.db_engine.acquire() as conn:
                    await conn.execute(query)

    async def get_user(self):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(self.tbl_model).where(
                    self.tbl_model.c.sub == self.params.sub
                )
            )
            res = await async_result.fetchone()
            return res

    async def get_users(self, limit: int = 20, offset: int = 0):
        select_expression = self.tbl_model.select()
        select_expression = select_expression.limit(limit)
        select_expression = select_expression.offset(offset)

        async with self.db_engine.acquire() as conn:
            count_expression = select([func.count()]).select_from(self.tbl_model)
            rows = await conn.execute(count_expression)
            try:
                total_rows = [row async for row in rows][0][0]
            except IndexError:
                total_rows = 0

        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(select_expression)
            res = await async_result.fetchall()
            return res, total_rows

    async def is_account_login_exist(self):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(self.tbl_model.c.account_login).where(
                    self.tbl_model.c.sub == self.params.sub
                )
            )
            return bool(await async_result.scalar())

    async def get_account_login(self):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(self.tbl_model.c.account_login).where(
                    self.tbl_model.c.sub == self.params.sub
                )
            )
            return await async_result.scalar()

    async def update_stratagy_buy(self, account_login: int,):
        async with self.db_engine.acquire() as conn:
            res_update = await conn.execute(
                self.tbl_model.update()
                .values(
                    {
                        "is_stratagy_buy": True,
                        "account_login": account_login
                    }
                )
                .where(self.tbl_model.c.sub == self.params.sub)
                .returning(self.tbl_model)
            )
            return await res_update.fetchone()

    async def update_subscription_buy(self):
        async with self.db_engine.acquire() as conn:
            res_update = await conn.execute(
                self.tbl_model.update()
                .values({"is_subscription_buy": True})
                .where(self.tbl_model.c.sub == self.params.sub)
                .returning(self.tbl_model)
            )
            return await res_update.fetchone()

    async def confirm_stratagy_payment(self, id: int):
        async with self.db_engine.acquire() as conn:
            res_update = await conn.execute(
                self.tbl_model.update()
                .values({"is_confirm_stratagy": True})
                .where(self.tbl_model.c.id == id)
                .returning(self.tbl_model)
            )
            return await res_update.fetchone()

    async def confirm_subscription_payment(self, id: int):
        async with self.db_engine.acquire() as conn:
            res_update = await conn.execute(
                self.tbl_model.update()
                .values({"is_confirm_subscription": True})
                .where(self.tbl_model.c.id == id)
                .returning(self.tbl_model)
            )
            return await res_update.fetchone()
