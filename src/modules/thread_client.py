import asyncio
import concurrent.futures


class ThreadClient:
    def __init__(self, n_workers=2):
        self.n_workers = n_workers
        self.executor = concurrent.futures.ThreadPoolExecutor(self.n_workers)
        self.loop = asyncio.get_running_loop()

    async def close(self):
        """
        Close treads
        """
        self.executor.shutdown(wait=True)

    async def exec(self, func, *args):
        """
        Exec func in treads
        """
        result = await self.loop.run_in_executor(self.executor, func, *args)
        return result
