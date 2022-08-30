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
from typing import Optional

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
        if self.http._session:
            await self.http._session.close()

    async def create_paste(
        self,
        *,
        filename: str,
        content: str,
        password: Optional[str] = None,
        expires: Optional[datetime.datetime] = None,
    ) -> Paste:
        """|coro|

        Create a single file paste on mystb.in.

        Parameters
        -----------
        filename: :class:`str`
            The filename to create.
        content: :class:`str`
            The content of the file you are creating.
        password: Optional[:class:`str`]
            The password of the paste, if any.
        expires: Optional[:class:`datetime.datetime`]
            When the paste expires, if any.

        Returns
        --------
        :class:`mystbin.Paste`
            The paste that was created.
        """
        file = File(filename=filename, content=content)
        data = await self.http._create_paste(file=file, password=password, expires=expires)
        return Paste._from_data(data)

    async def create_multifile_paste(
        self, *, files: list[File], password: Optional[str] = None, expires: Optional[datetime.datetime] = None
    ) -> Paste:
        """|coro|

        Create a paste with multiple files on mystb.in.

        Parameters
        ------------
        files: list[:class:`mystbin.File`]
            A list of files to create on mystbin.
        password: Optional[:class:`str`]
            The password for this paste, if any.
        expires: Optional[:class:`datetime.datetime`]
            When this paste expires, if any.

        Returns
        --------
        :class:`mystbin.Paste`
            The paste that was created.
        """
        data = await self.http._create_paste(files=files, password=password, expires=expires)
        return Paste._from_data(data)

    @require_authentication
    async def delete_paste(self, paste_id: str, /) -> None:
        """|coro|

        Delete a paste.

        Parameters
        -----------
        paste_id: :class:`str`
            The paste to delete.
        """
        await self.http._delete_pastes(paste_ids=[paste_id])

    @require_authentication
    async def delete_pastes(self, paste_ids: list[str], /) -> None:
        """|coro|

        Delete multiple pastes.

        Parameters
        -----------
        paste_ids: list[:class:`str`]
            The pastes to delete.
        """
        await self.http._delete_pastes(paste_ids=paste_ids)

    async def get_paste(self, paste_id: str, *, password: Optional[str] = None) -> Paste:
        """|coro|

        Fetch a paste.

        Parameters
        -----------
        paste_id: :class:`str`
            The paste id to fetch.
        password: Optional[:class:`str`]
            The password of the paste, if any.
        """
        data = await self.http._get_paste(paste_id=paste_id, password=password)
        return Paste._from_data(data)

    # @overload
    # async def edit_paste(self, paste_id: str, *, new_content: str, new_filename: ..., new_expires: ...) -> None:
    #     ...

    # @overload
    # async def edit_paste(self, paste_id: str, *, new_content: ..., new_filename: str, new_expires: ...) -> None:
    #     ...

    # @overload
    # async def edit_paste(
    #     self, paste_id: str, *, new_content: ..., new_filename: ..., new_expires: datetime.datetime
    # ) -> None:
    #     ...

    # @overload
    # async def edit_paste(self, paste_id: str, *, new_content: str, new_filename: str, new_expires: ...) -> None:
    #     ...

    # @overload
    # async def edit_paste(
    #     self, paste_id: str, *, new_content: str, new_filename: ..., new_expires: datetime.datetime
    # ) -> None:
    #     ...

    # @overload
    # async def edit_paste(
    #     self, paste_id: str, *, new_content: ..., new_filename: str, new_expires: datetime.datetime
    # ) -> None:
    #     ...

    # @overload
    # async def edit_paste(
    #     self, paste_id: str, *, new_content: str, new_filename: str, new_expires: datetime.datetime
    # ) -> None:
    #     ...

    # @require_authentication
    # async def edit_paste(
    #     self,
    #     paste_id: str,
    #     *,
    #     new_content: Optional[str] = MISSING,
    #     new_filename: Optional[str] = MISSING,
    #     new_expires: Optional[datetime.datetime] = MISSING,
    # ) -> None:
    #     await self.http._edit_paste(paste_id, new_content=new_content, new_filename=new_filename, new_expires=new_expires)

    @require_authentication
    async def get_user_pastes(self, *, limit: int = 100) -> list[Paste]:
        """|coro|

        Get all pastes belonging to the current authenticated user.

        Parameters
        -----------
        limit: :class:`int`
            The amount of pastes to fetch. Defaults to ``100``.

        Returns
        --------
        list[:class:`Paste`]
            The pastes that were fetched.
        """
        data = await self.http._get_my_pastes(limit=limit)

        return [Paste._from_data(x) for x in data]
