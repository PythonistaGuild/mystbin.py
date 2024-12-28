"""
The MIT License (MIT)

Copyright (c) 2020 - Present, PythonistaGuild

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""  # noqa: A005 # we access this via namespace

from __future__ import annotations

import asyncio
import datetime
import json
import logging
import sys
import weakref
from typing import (
    TYPE_CHECKING,
    Any,
    ClassVar,
    Coroutine,
    Literal,
    Sequence,
    TypeVar,
)
from urllib.parse import quote as _uriquote

import aiohttp

from . import __version__
from .errors import APIException

if TYPE_CHECKING:
    from types import TracebackType

    from . import File

    T = TypeVar("T")
    Response = Coroutine[None, None, T]
    MU = TypeVar("MU", bound="MaybeUnlock")
    from .types.responses import CreatePasteResponse, GetPasteResponse


SupportedHTTPVerb = Literal["GET", "POST", "PUT", "DELETE", "PATCH"]

LOGGER: logging.Logger = logging.getLogger(__name__)

__all__ = ("HTTPClient",)


def _clean_dt(dt: datetime.datetime) -> str:
    dt = dt.astimezone(datetime.timezone.utc)

    return dt.isoformat()


async def _json_or_text(response: aiohttp.ClientResponse, /) -> dict[str, Any] | str:
    """A quick method to parse a `aiohttp.ClientResponse` and test if it's json or text.

    Returns
    --------
    Union[Dict[:class:`str`, Any], :class:`str`]
        The JSON object, or request text.
    """
    text = await response.text(encoding="utf-8")
    try:
        if response.headers["content-type"] == "application/json":
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                pass
    except KeyError:
        pass

    return text


class MaybeUnlock:
    def __init__(self, lock: asyncio.Lock) -> None:
        self.lock: asyncio.Lock = lock
        self._unlock: bool = True

    def __enter__(self: MU) -> MU:
        return self

    def defer(self) -> None:
        self._unlock = False

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        if self._unlock:
            self.lock.release()


class Route:
    __slots__ = (
        "path",
        "url",
        "verb",
    )

    API_BASE: ClassVar[str] = "https://mystb.in/api"

    def __init__(self, verb: SupportedHTTPVerb, path: str, **params: Any) -> None:
        self.verb: SupportedHTTPVerb = verb
        self.path: str = path
        url = self.API_BASE + path
        if params:
            url = url.format_map({k: _uriquote(v) if isinstance(v, str) else v for k, v in params.items()})
        self.url: str = url


class HTTPClient:
    __slots__ = (
        "_locks",
        "_owns_session",
        "_session",
        "_token",
        "root_url",
        "user_agent",
    )

    def __init__(self, *, session: aiohttp.ClientSession | None = None, root_url: str | None = None) -> None:
        self._session: aiohttp.ClientSession | None = session
        self._owns_session: bool = False
        self._locks: weakref.WeakValueDictionary[str, asyncio.Lock] = weakref.WeakValueDictionary()
        user_agent = "mystbin.py (https://github.com/PythonistaGuild/mystbin.py {0}) Python/{1[0]}.{1[1]} aiohttp/{2}"
        self.user_agent: str = user_agent.format(__version__, sys.version_info, aiohttp.__version__)
        self._resolve_api(root_url)

    def _resolve_api(self, root_url: str | None, /) -> None:
        if root_url:
            Route.API_BASE = root_url + "api" if root_url.endswith("/") else root_url + "/api"
            self.root_url = root_url + ("/" if not root_url.endswith("/") else "")
        else:
            self.root_url = "https://mystb.in/"

    async def close(self) -> None:
        if self._session and self._owns_session:
            await self._session.close()

    async def _generate_session(self) -> aiohttp.ClientSession:
        self._session = aiohttp.ClientSession()
        self._owns_session = True
        return self._session

    async def request(self, route: Route, **kwargs: Any) -> Any:
        if self._session is None:
            self._session = await self._generate_session()

        bucket = route.path
        lock = self._locks.get(bucket)
        if lock is None:
            lock = asyncio.Lock()
            self._locks[bucket] = lock

        headers = kwargs.pop("headers", {})
        headers["User-Agent"] = self.user_agent

        if "json" in kwargs:
            headers["Content-Type"] = "application/json"
            kwargs["data"] = json.dumps(kwargs.pop("json"), separators=(",", ":"), ensure_ascii=True)
            LOGGER.debug("Current json body is: %s", str(kwargs["data"]))

        kwargs["headers"] = headers

        LOGGER.debug("Current request headers: %s", headers)
        LOGGER.debug("Current request url: %s", route.url)

        response: aiohttp.ClientResponse | None = None
        await lock.acquire()
        with MaybeUnlock(lock) as maybe_lock:
            for tries in range(5):
                try:
                    async with self._session.request(route.verb, route.url, **kwargs) as response:
                        # Requests remaining before ratelimit
                        remaining = response.headers.get("x-ratelimit-remaining", None)
                        LOGGER.debug("remaining is: %s", remaining)
                        # Timestamp for when current ratelimit session(?) expires
                        retry = response.headers.get("x-ratelimit-retry-after", None)
                        LOGGER.debug("retry is: %s", retry)
                        if retry is not None:
                            retry = datetime.datetime.fromtimestamp(int(retry), tz=datetime.timezone.utc)
                        # The total ratelimit session hits
                        limit = response.headers.get("x-ratelimit-limit", None)
                        LOGGER.debug("limit is: %s", limit)

                        if remaining == "0" and response.status != 429:
                            assert retry is not None
                            delta = retry - datetime.datetime.now(datetime.timezone.utc)
                            sleep = delta.total_seconds() + 1
                            LOGGER.warning("A ratelimit has been exhausted, sleeping for: %d", sleep)
                            maybe_lock.defer()
                            loop = asyncio.get_running_loop()
                            loop.call_later(sleep, lock.release)

                        data = await _json_or_text(response)

                        if 300 > response.status >= 200:
                            return data

                        if response.status == 429:
                            assert retry is not None
                            delta = retry - datetime.datetime.now(datetime.timezone.utc)
                            sleep = delta.total_seconds() + 1
                            LOGGER.warning("A ratelimit has been hit, sleeping for: %d", sleep)
                            await asyncio.sleep(sleep)
                            continue

                        if response.status in {500, 502, 503, 504}:
                            sleep_ = 1 + tries * 2
                            LOGGER.warning("Hit an API error, trying again in: %d", sleep_)
                            await asyncio.sleep(sleep_)
                            continue

                        assert isinstance(data, dict)
                        LOGGER.exception("Unhandled HTTP error occurred: %s -> %s", response.status, data)
                        raise APIException(
                            response=response,
                            status_code=response.status,
                        )
                except (aiohttp.ServerDisconnectedError, aiohttp.ServerTimeoutError):
                    LOGGER.exception("Network error occurred:")
                    await asyncio.sleep(5)
                    continue

            if response is not None:
                if response.status >= 500:
                    raise APIException(response=response, status_code=response.status)

                raise APIException(response=response, status_code=response.status)

            raise RuntimeError("Unreachable code in HTTP handling.")

    def create_paste(
        self,
        *,
        files: Sequence[File],
        password: str | None,
        expires: datetime.datetime | None,
    ) -> Response[CreatePasteResponse]:
        route = Route("POST", "/paste")

        json_: dict[str, Any] = {}
        json_["files"] = [f.to_dict() for f in files]

        if password:
            json_["password"] = password
        if expires:
            json_["expires"] = _clean_dt(expires)

        return self.request(route=route, json=json_)

    def delete_paste(self, security_token: str, /) -> Response[bool]:
        route = Route("GET", "/security/delete/{security_token}", security_token=security_token)
        return self.request(route)

    def get_paste(self, *, paste_id: str, password: str | None) -> Response[GetPasteResponse]:
        route = Route("GET", "/paste/{paste_id}", paste_id=paste_id)

        if password:
            return self.request(route=route, params={"password": password})
        return self.request(route=route)
