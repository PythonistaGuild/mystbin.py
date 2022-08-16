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
from typing import Optional, overload

import aiohttp

from .http import HTTPClient
from .paste import File, Paste
from .utils import MISSING, require_authentication


__all__ = ("Client",)


class Client:
    __slots__ = ("http",)

    def __init__(self, *, token: Optional[str] = None, session: Optional[aiohttp.ClientSession] = None) -> None:
        self.http = HTTPClient(token=token, session=session)

    async def create_paste(
        self,
        *,
        filename: str,
        content: str,
        syntax: Optional[str] = None,
        password: Optional[str] = None,
        expires: Optional[datetime.datetime] = None,
    ) -> Paste:
        file = File(filename=filename, content=content, syntax=syntax)
        data = await self.http._create_paste(file=file, password=password, expires=expires)
        return Paste.from_data(data)

    async def create_multifile_paste(
        self, *, files: list[File], password: Optional[str] = None, expires: Optional[datetime.datetime] = None
    ) -> Paste:
        data = await self.http._create_paste(files=files, password=password, expires=expires)
        return Paste.from_data(data)

    @require_authentication
    async def delete_paste(self, paste_id: str, /) -> None:
        await self.http._delete_pastes(paste_ids=[paste_id])

    @require_authentication
    async def delete_pastes(self, paste_ids: list[str], /) -> None:
        await self.http._delete_pastes(paste_ids=paste_ids)

    async def get_paste(self, *, paste_id: str, password: Optional[str] = None) -> Paste:
        data = await self.http._get_paste(paste_id=paste_id, password=password)
        return Paste.from_data(data)

    @overload
    async def edit_paste(self, paste_id: str, *, new_content: str, new_filename: ..., new_expires: ...) -> None:
        ...

    @overload
    async def edit_paste(self, paste_id: str, *, new_content: ..., new_filename: str, new_expires: ...) -> None:
        ...

    @overload
    async def edit_paste(
        self, paste_id: str, *, new_content: ..., new_filename: ..., new_expires: datetime.datetime
    ) -> None:
        ...

    @overload
    async def edit_paste(self, paste_id: str, *, new_content: str, new_filename: str, new_expires: ...) -> None:
        ...

    @overload
    async def edit_paste(
        self, paste_id: str, *, new_content: str, new_filename: ..., new_expires: datetime.datetime
    ) -> None:
        ...

    @overload
    async def edit_paste(
        self, paste_id: str, *, new_content: ..., new_filename: str, new_expires: datetime.datetime
    ) -> None:
        ...

    @overload
    async def edit_paste(
        self, paste_id: str, *, new_content: str, new_filename: str, new_expires: datetime.datetime
    ) -> None:
        ...

    @require_authentication
    async def edit_paste(
        self,
        paste_id: str,
        *,
        new_content: Optional[str] = MISSING,
        new_filename: Optional[str] = MISSING,
        new_expires: Optional[datetime.datetime] = MISSING,
    ) -> None:
        await self.http._edit_paste(paste_id)

    @require_authentication
    async def get_user_pastes(self, *, limit: int = 100) -> list[Paste]:
        data = await self.http._get_my_pastes(limit=limit)

        return [Paste.from_data(x) for x in data]
