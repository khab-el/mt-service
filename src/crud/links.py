from sqlalchemy.sql import select
from aiopg.sa import Engine
from sqlalchemy import MetaData


class Link:
    def __init__(self, db_engine: Engine, db_meta: MetaData) -> None:
        self.db_engine = db_engine
        self.db_meta = db_meta
        self.tbl_model = db_meta.tables["links"]

    async def get_referal_by_user(self, source: int):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(self.tbl_model).where(
                    self.tbl_model.c.source == source
                )
            )
            res = await async_result.fetchall()
            return res
