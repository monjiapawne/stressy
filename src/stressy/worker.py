import asyncio
from asyncio import AbstractEventLoop
from collections.abc import Callable
from concurrent.futures import Future

from aiohttp import ClientError, ClientSession


class RequestJob:
    def __init__(self, loop: AbstractEventLoop, url: str, total_requests: int, callback: Callable) -> None:
        self._future: Future | None = None
        self._loop = loop
        self._url = url
        self._callback: Callable[[int, int, set[int]]] = callback
        self._total_requests = total_requests
        self._done = 0
        self._failed = 0
        self._error_codes: set[int] = set()

    def submit(self):
        self._future = asyncio.run_coroutine_threadsafe(self._make_reqs(), self._loop)

    def cancel(self):
        if self._future:
            self._future.cancel()

    async def _make_reqs(self):
        async with ClientSession() as session:
            await asyncio.gather(*(self._make_one_request(session) for _ in range(self._total_requests)))

    async def _make_one_request(self, s: ClientSession):
        try:
            async with s.get(self._url) as rsp:
                if not rsp.ok:
                    self._failed += 1
                    self._error_codes.add(rsp.status)
        except (ClientError, TimeoutError):
            self._failed += 1

        self._done += 1
        self._callback(self._done, self._failed, self._error_codes)
