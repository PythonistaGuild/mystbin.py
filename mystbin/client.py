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

import datetime
from typing import List, Literal, Optional, Sequence, Union, overload

import aiohttp

from .http import HTTPClient
from .paste import File, Paste
from .utils import require_authentication


__all__ = ("Client",)


class Client:
    __slots__ = ("http",)

    def __init__(self, *, token: Optional[str] = None, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.http: HTTPClient = HTTPClient(token=token, session=session)

    async def close(self) -> None:
        """|coro|

        Closes the internal HTTP session and this client.
        """
        await self.http.close()

    @overload
    async def create_paste(
        self,
        *,
        filename: str,
        content: str,
        file: None = ...,
        files: None = ...,
        password: Optional[str] = ...,
        expires: Optional[datetime.datetime] = ...,
    ) -> Paste:
        ...

    @overload
    async def create_paste(
        self,
        *,
        filename: None = ...,
        content: None = ...,
        file: File,
        files: None = ...,
        password: Optional[str] = ...,
        expires: Optional[datetime.datetime] = ...,
    ) -> Paste:
        ...

    @overload
    async def create_paste(
        self,
        *,
        filename: None = ...,
        content: None = ...,
        file: None = ...,
        files: Sequence[File],
        password: Optional[str] = ...,
        expires: Optional[datetime.datetime] = ...,
    ) -> Paste:
        ...

    async def create_paste(
        self,
        *,
        filename: Optional[str] = None,
        content: Optional[str] = None,
        file: Optional[File] = None,
        files: Optional[Sequence[File]] = None,
        password: Optional[str] = None,
        expires: Optional[datetime.datetime] = None,
    ) -> Paste:
        """|coro|

        Create a single file paste on mystb.in.

        Parameters
        -----------
        filename: Optional[:class:`str`]
            The filename to create.
        content: Optional[:class:`str`]
            The content of the file you are creating.
        file: Optional[:class:`~mystbin.File`]
            The pre-created file you wish to upload.
        files: Optional[List[:class:`~mystbin.File`]]
            The pre-creates list of files you wish to upload.
        password: Optional[:class:`str`]
            The password of the paste, if any.
        expires: Optional[:class:`datetime.datetime`]
            When the paste expires, if any.

        Raises
        -------
        :exc:`ValueError`
            A bad combinarion of singular and plural pastes were passed.

        Returns
        --------
        :class:`mystbin.Paste`
            The paste that was created.


        ..note::
            Passing combinations of both singular and plural files is not supports and will raise an exception.
            Internally the order of precesence is ``files`` > ``file`` > ``filename and content``.
        """
        if (filename and content) and file:
            raise ValueError("Cannot provide both `file` and `filename`/`content`")

        resolved_files: Sequence[File] = []
        if filename and content:
            resolved_files = [File(filename=filename, content=content, attachment_url=None)]
        elif file:
            resolved_files = [file]

        if resolved_files and files:
            raise ValueError("Cannot provide both singular and plural files.")

        resolved_files = files or resolved_files

        data = await self.http.create_paste(files=resolved_files, password=password, expires=expires)
        return Paste.from_data(data)

    @require_authentication
    async def delete_paste(self, paste_id: str, /) -> None:
        """|coro|

        Delete a paste.

        Parameters
        -----------
        paste_id: :class:`str`
            The paste to delete.
        """
        await self.http.delete_pastes(paste_ids=[paste_id])

    @require_authentication
    async def delete_pastes(self, paste_ids: List[str], /) -> None:
        """|coro|

        Delete multiple pastes.

        Parameters
        -----------
        paste_ids: List[:class:`str`]
            The pastes to delete.
        """
        await self.http.delete_pastes(paste_ids=paste_ids)

    @overload
    async def get_paste(self, paste_id: str, *, password: Optional[str] = ..., raw: Literal[False]) -> Paste:
        ...

    @overload
    async def get_paste(self, paste_id: str, *, password: Optional[str] = ..., raw: Literal[True]) -> list[str]:
        ...

    async def get_paste(
        self, paste_id: str, *, password: Optional[str] = None, raw: bool = False
    ) -> Union[Paste, list[str]]:
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
        return Paste.from_data(data)

    @require_authentication
    async def get_user_pastes(self, *, limit: int = 100) -> List[Paste]:
        """|coro|

        Get all pastes belonging to the current authenticated user.

        Parameters
        -----------
        limit: :class:`int`
            The amount of pastes to fetch. Defaults to ``100``.

        Returns
        --------
        List[:class:`Paste`]
            The pastes that were fetched.
        """
        data = await self.http.get_my_pastes(limit=limit)

        return [Paste.from_data(x) for x in data]
