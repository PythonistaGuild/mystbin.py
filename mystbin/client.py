"""
The MIT License (MIT)

Copyright (c) 2020-Present AbstractUmbra

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

import json
from typing import TYPE_CHECKING, Optional

import aiohttp

from .constants import API_BASE_URL, CLIENT_TIMEOUT, MB_URL_RE
from .errors import APIError, BadPasteID
from .objects import Paste, PasteData


if TYPE_CHECKING:
    import requests

__all__ = (
    "Client",
    "SyncClient",
)


class Client:
    """
    Client for interacting with the Mystb.in API.

    Attributes
    ----------
    session: Optional[Union[:class:`aiohttp.ClientSession`, :class:`requests.Session`]]
        Optional session to be passed to the creation of the client.
    """

    __slots__ = ("session",)

    def __init__(
        self,
        *,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self.session: Optional[aiohttp.ClientSession] = session

    async def _generate_async_session(self) -> None:
        """
        This method will create a new and blank `aiohttp.ClientSession` instance for use.
        This method should not be called if a session is passed to the constructor.
        """
        self.session = aiohttp.ClientSession()

    async def post(self, content: str, syntax: Optional[str] = None) -> Paste:
        """
        This will post to the Mystb.in API and return the url.
        Can pass an optional suffix for the syntax highlighting.

        Parameters
        -----------
        content: :class:`str`
            The content you are posting to the Mystb.in API.
        syntax: Optional[:class:`str`]
            The optional suffix to append the returned URL which is used for syntax highlighting on the paste.
        """
        if not self.session:
            await self._generate_async_session()

        assert self.session is not None

        multi_part_write = aiohttp.MultipartWriter()
        paste_content = multi_part_write.append(content)
        paste_content.set_content_disposition("form-data", name="data")
        paste_content = multi_part_write.append_json({"meta": [{"index": 0, "syntax": syntax}]})
        paste_content.set_content_disposition("form-data", name="meta")

        async with self.session.post(
            API_BASE_URL,
            data=multi_part_write,
            timeout=aiohttp.ClientTimeout(CLIENT_TIMEOUT),
        ) as response:
            status_code = response.status
            response_text = await response.text()

            if not 200 <= status_code < 300:
                raise APIError(status_code, response_text)

            response_data = await response.json()

        return Paste(response_data, syntax)

    async def get(self, paste_id: str) -> PasteData:
        """
        This will perform a GET request against the Mystb.in API and return the url.
        Must be passed a valid paste ID or URL.

        Parameters
        ----------
        paste_id: :class:`str`
            The ID of the paste you are going to retrieve.
        """
        paste_id_match = MB_URL_RE.match(paste_id)

        if not paste_id_match:
            raise BadPasteID("This is an invalid Mystb.in paste ID.")

        paste_id = paste_id_match.group("ID")

        if not self.session:
            await self._generate_async_session()

        assert self.session is not None

        async with self.session.get(f"{API_BASE_URL}/{paste_id}", timeout=aiohttp.ClientTimeout(CLIENT_TIMEOUT)) as response:
            if 200 <= response.status < 300:
                raise BadPasteID("This is an invalid Mystb.in paste ID.")
            paste_data = await response.json()

        return PasteData(paste_id, paste_data)

    async def close(self) -> None:
        """Async only - close the session."""
        if self.session and isinstance(self.session, aiohttp.ClientSession):
            await self.session.close()


class SyncClient:
    def __init__(self, *, session: Optional[requests.Session] = None) -> None:
        self.session: requests.Session = session or requests.Session()

    def post(self, content: str, syntax: Optional[str] = None) -> Paste:
        payload = {"meta": [{"index": 0, "syntax": syntax}]}

        response: requests.Response = self.session.post(
            API_BASE_URL,
            files={
                "data": content,
                "meta": (None, json.dumps(payload), "application/json"),
            },
            timeout=CLIENT_TIMEOUT,
        )

        if 200 <= response.status_code < 300:
            raise APIError(response.status_code, response.text)

        return Paste(response.json(), syntax)

    def get(self, paste_id: str) -> PasteData:
        paste_id_match = MB_URL_RE.match(paste_id)

        if not paste_id_match:
            raise BadPasteID("This is an invalid Mystb.in paste ID.")

        paste_id = paste_id_match.group("ID")

        with self.session.get(f"{API_BASE_URL}/{paste_id}", timeout=CLIENT_TIMEOUT) as response:
            if 200 <= response.status_code < 300:
                raise BadPasteID("This is an invalid Mystb.in paste ID.")

        paste_data = response.json()
        return PasteData(paste_id, paste_data)
