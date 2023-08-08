import time
from uuid import uuid4

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql as sa_pg


def reflect_meta(dsn: str):
    engine = sa.create_engine(dsn, pool_size=1)
    meta = sa.MetaData(bind=engine)
    meta.reflect()
    engine.dispose()

    # fix uuid
    for table in meta.tables.values():
        for col in table.columns:
            if isinstance(col.type, sa_pg.base.UUID):
                col.type.as_uuid = True

    return meta


async def iter_cursor(db, query, params, batch_size=1_000, cur_name_=None):
    cur_name = f"cur_{cur_name_ or uuid4().hex}_{time.time_ns()}"
    query_cursor = f"DECLARE {cur_name} CURSOR FOR {query}"
    query_next_page = f"FETCH %(batch_size)s FROM {cur_name}"
    params_next_page = {"batch_size": batch_size}

    async with db.acquire() as conn:
        async with conn.begin(readonly=True):
            await conn.execute(query_cursor, params)

            while True:
                res = await conn.execute(query_next_page, params_next_page)
                batch = await res.fetchall()
                if not len(batch):
                    return
                yield batch