import datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy.sql import select, func
from aiopg.sa import Engine
from sqlalchemy import MetaData
from sqlalchemy.sql.expression import true


class Orders:
    def __init__(self, db_engine: Engine, db_meta: MetaData) -> None:
        self.db_engine = db_engine
        self.db_meta = db_meta
        self.tbl_model = db_meta.tables["orders"]

    async def get_orders(self, account_login: int, order_is_closed: bool, limit: int = 20, offset: int = 0):
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
            async_result = await conn.execute(
                select(self.tbl_model).where(
                    self.tbl_model.c.account_login == account_login,
                    self.tbl_model.c.order_is_closed == order_is_closed
                )
            )
            res = await async_result.fetchall()
            return res, total_rows

    async def get_predicted_profit(self, account_login: int):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(
                    [
                        self.tbl_model.c.order_symbol,
                        func.sum(self.tbl_model.c.order_profit).label('predict_profit')
                    ]
                )
                .where(
                    self.tbl_model.c.account_login == account_login
                )
                .group_by(self.tbl_model.c.account_login, self.tbl_model.c.order_symbol)
            )
            res = await async_result.fetchall()
            return res

    async def get_profit(self, account_login: int):
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(
                select(
                    [
                        self.tbl_model.c.order_symbol,
                        func.sum(self.tbl_model.c.order_profit).label('profit')
                    ]
                )
                .where(
                    self.tbl_model.c.account_login == account_login,
                    self.tbl_model.c.order_is_closed == true()
                )
                .group_by(self.tbl_model.c.account_login, self.tbl_model.c.order_symbol)
            )
            res = await async_result.fetchall()
            return res

    async def get_chart(self, account_login, chart_type):
        now = datetime.datetime.now()
        now = now.replace(hour=0, minute=0, second=0, microsecond=0)

        if chart_type == 'day':
            sql_filter = "order_time::date as closed_day"
            closed_time_filter = f"and order_time > '{str((now - relativedelta(month=+2)).date())}'"
        elif chart_type == 'week':
            sql_filter = "date_trunc('week', order_time) as closed_week"
            closed_time_filter = f"and order_time > '{str((now - relativedelta(year=+1)).date())}'"
        elif chart_type == 'month':
            sql_filter = "date_trunc('month', order_time) as closed_month"
            closed_time_filter = ""
        elif chart_type == 'year':
            sql_filter = "date_trunc('year', order_time) as closed_year"
            closed_time_filter = ""

        sql = f"""
        select
            {sql_filter},
            sum(order_profit) filter (where order_symbol = 'GBPUSD') as GBPUSD,
            sum(order_profit) filter (where order_symbol = 'USDCAD') as USDCAD,
            sum(order_profit) filter (where order_symbol = 'EURGBP') as EURGBP,
            sum(order_profit) filter (where order_symbol = 'CADCHF') as CADCHF,
            sum(order_profit) filter (where order_symbol = 'NZDUSD') as NZDUSD,
            sum(order_profit) filter (where order_symbol = 'AUDCHF') as AUDCHF,
            sum(order_profit) filter (where order_symbol = 'NZDCAD') as NZDCAD,
            sum(order_profit) filter (where order_symbol = 'AUDUSD') as AUDUSD,
            sum(order_profit) filter (where order_symbol = 'AUDCAD') as AUDCAD,
            sum(order_profit) filter (where order_symbol = 'GBPCAD') as GBPCAD,
            sum(order_profit) filter (where order_symbol = 'EURJPY') as EURJPY,
            sum(order_profit) filter (where order_symbol = 'AUDJPY') as AUDJPY
        from orders
        where account_login = {account_login}
            {closed_time_filter}
            and order_is_closed = true
        group by closed_{chart_type}
        """
        async with self.db_engine.acquire() as conn:
            async_result = await conn.execute(sql)
            res = await async_result.fetchall()
            return res

    async def prepare_chart(self, account_login: int, chart_type: str):
        chart = await self.get_chart(account_login, chart_type)

        now = datetime.datetime.now()
        now = now.replace(hour=0, minute=0, second=0, microsecond=0)
        # curr date
        if chart_type == 'day':
            curr_date = now
            prev_date = (curr_date - datetime.timedelta(days=1))
        elif chart_type == 'week':
            curr_date = now - datetime.timedelta(days=now.weekday())
            prev_date = (curr_date - datetime.timedelta(days=7))
        elif chart_type == 'month':
            curr_date = now.replace(day=1)
            prev_date = (curr_date - datetime.timedelta(days=1)).replace(day=1)
        elif chart_type == 'year':
            curr_date = now.replace(month=1, day=1)
            prev_date = (curr_date - datetime.timedelta(days=1)).replace(month=1, day=1)

        prev_date = prev_date
        curr_date = curr_date

        lst = []
        curr_prev = {}
        for row in chart:
            if chart_type == 'month':
                date = row['closed_month']
            elif chart_type == 'day':
                date = row['closed_day']
            elif chart_type == 'year':
                date = row['closed_year']
            elif chart_type == 'week':
                date = row['closed_week']
            d = {
                date: {
                    'GBPUSD': row['gbpusd'],
                    'USDCAD': row['usdcad'],
                    'EURGBP': row['eurgbp'],
                    'CADCHF': row['cadchf'],
                    'NZDUSD': row['nzdusd'],
                    'AUDCHF': row['audchf'],
                    'NZDCAD': row['nzdcad'],
                    'AUDUSD': row['audusd'],
                    'AUDCAD': row['audcad'],
                    'GBPCAD': row['gbpcad'],
                    'EURJPY': row['eurjpy'],
                    'AUDJPY': row['audjpy'],
                }
            }
            lst.append(d)

            if date == curr_date:
                cur = {
                    'GBPUSD': row['gbpusd'] if row['gbpusd'] is not None else 0,
                    'USDCAD': row['usdcad'] if row['usdcad'] is not None else 0,
                    'EURGBP': row['eurgbp'] if row['eurgbp'] is not None else 0,
                    'CADCHF': row['cadchf'] if row['cadchf'] is not None else 0,
                    'NZDUSD': row['nzdusd'] if row['nzdusd'] is not None else 0,
                    'AUDCHF': row['audchf'] if row['audchf'] is not None else 0,
                    'NZDCAD': row['nzdcad'] if row['nzdcad'] is not None else 0,
                    'AUDUSD': row['audusd'] if row['audusd'] is not None else 0,
                    'AUDCAD': row['audcad'] if row['audcad'] is not None else 0,
                    'GBPCAD': row['gbpcad'] if row['gbpcad'] is not None else 0,
                    'EURJPY': row['eurjpy'] if row['eurjpy'] is not None else 0,
                    'AUDJPY': row['audjpy'] if row['audjpy'] is not None else 0,
                }
                curr_prev["curr_date"] = cur
            elif date == prev_date:
                prev = {
                    'GBPUSD': row['gbpusd'] if row['gbpusd'] is not None else 1,
                    'USDCAD': row['usdcad'] if row['usdcad'] is not None else 1,
                    'EURGBP': row['eurgbp'] if row['eurgbp'] is not None else 1,
                    'CADCHF': row['cadchf'] if row['cadchf'] is not None else 1,
                    'NZDUSD': row['nzdusd'] if row['nzdusd'] is not None else 1,
                    'AUDCHF': row['audchf'] if row['audchf'] is not None else 1,
                    'NZDCAD': row['nzdcad'] if row['nzdcad'] is not None else 1,
                    'AUDUSD': row['audusd'] if row['audusd'] is not None else 1,
                    'AUDCAD': row['audcad'] if row['audcad'] is not None else 1,
                    'GBPCAD': row['gbpcad'] if row['gbpcad'] is not None else 1,
                    'EURJPY': row['eurjpy'] if row['eurjpy'] is not None else 1,
                    'AUDJPY': row['audjpy'] if row['audjpy'] is not None else 1,
                }
                curr_prev["prev_date"] = prev

        return lst, curr_prev
