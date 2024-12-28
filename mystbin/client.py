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
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Literal, Sequence, overload

from .http import HTTPClient
from .paste import File, Paste

if TYPE_CHECKING:
    import datetime
    from types import TracebackType

    from aiohttp import ClientSession
    from typing_extensions import Self

__all__ = ("Client",)


class Client:
    """
    The main client class that interacts with the mystb.in API.

    Parameters
    -----------
    session: Optional[:class:`aiohttp.ClientSession`]
        The session to use for the HTTP requests.
        If not provided, a new session will be created.
    api_base: :class:`str`
        The base URL for the mystbin instance.
        Defaults to ``mystb.in``.
    """

    __slots__ = ("http",)

    def __init__(self, *, session: ClientSession | None = None, api_base: str = "mystb.in") -> None:
        self.http: HTTPClient = HTTPClient(session=session, api_base=api_base)

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_cls: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.close()

    async def close(self) -> None:
        """|coro|

        Closes the internal HTTP session and this client.
        """
        await self.http.close()

    async def create_paste(
        self,
        *,
        files: Sequence[File],
        password: str | None = None,
        expires: datetime.datetime | None = None,
    ) -> Paste:
        """|coro|

        Create a single file paste on mystb.in.

        Parameters
        -----------
        files: List[:class:`~mystbin.File`]
            The pre-creates list of files you wish to upload.
        password: Optional[:class:`str`]
            The password of the paste, if any.
        expires: Optional[:class:`datetime.datetime`]
            When the paste expires, if any.

        Returns
        --------
        :class:`mystbin.Paste`
            The paste that was created.
        """
        data = await self.http.create_paste(files=files, password=password, expires=expires)
        return Paste.from_create(data, files=files, http=self.http)

    async def delete_paste(self, security_token: str, /) -> None:
        """|coro|

        Delete a paste.

        Parameters
        -----------
        security_token: :class:`str`
            The security token relating to the paste to delete.
        """
        await self.http.delete_paste(security_token)

    @overload
    async def get_paste(self, paste_id: str, *, password: str | None = ..., raw: Literal[False]) -> Paste: ...

    @overload
    async def get_paste(self, paste_id: str, *, password: str | None = ..., raw: Literal[True]) -> list[str]: ...

    @overload
    async def get_paste(self, paste_id: str, *, password: str | None = ...) -> Paste: ...

    async def get_paste(self, paste_id: str, *, password: str | None = None, raw: bool = False) -> Paste | list[str]:
        """|coro|

        Fetch a paste.

        Parameters
        -----------
        paste_id: :class:`str`
            The paste id to fetch.
        password: Optional[:class:`str`]
            The password of the paste, if any.
        raw: :class:`bool`
            Whether to return the raw file(s) content or a :class:`~mystbin.Paste` instance.
            Defaults to ``False``.

        Returns
        --------
        Union[:class:`~mystbin.Paste`, List[:class:`str`]]
            The paste data returned.
        """
        data = await self.http.get_paste(paste_id=paste_id, password=password)
        if raw:
            return [item["content"] for item in data["files"]]
        return Paste.from_get(data, http=self.http)
