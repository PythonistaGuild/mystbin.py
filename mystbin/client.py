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
from typing import TYPE_CHECKING, Coroutine, Optional, Union

import aiohttp

from .constants import API_BASE_URL, CLIENT_TIMEOUT, MB_URL_RE
from .errors import APIError, BadPasteID
from .objects import Paste, PasteData


if TYPE_CHECKING:
    import requests

__all__ = ("HTTPClient",)


class HTTPClient:
    """
    Client for interacting with the Mystb.in API.

    Attributes
    ----------
    session: Optional[Union[:class:`aiohttp.ClientSession`, :class:`requests.Session`]]
        Optional session to be passed to the creation of the client.
    """

    __slots__ = (
        "session",
        "_are_we_async",
    )

    def __init__(
        self,
        *,
        session: Optional[Union[aiohttp.ClientSession, requests.Session]] = None,
    ) -> None:
        self._are_we_async = session is None or isinstance(session, aiohttp.ClientSession)
        self.session = session  # type: ignore

    async def _generate_async_session(self) -> None:
        """
        This method will create a new and blank `aiohttp.ClientSession` instance for use.
        This method should not be called if a session is passed to the constructor.
        """
        self.session: aiohttp.ClientSession = aiohttp.ClientSession()

    def post(self, content: str, syntax: str = None) -> Union[Paste, Coroutine[None, None, Paste]]:
        """
        This will post to the Mystb.in API and return the url.
        Can pass an optional suffix for the syntax highlighting.

        Parameters
        -----------
        content: :class:`str`
            The content you are posting to the Mystb.in API.
        syntax: :class:`str`
            The optional suffix to append the returned URL which is used for syntax highlighting on the paste.
        """
        if self._are_we_async:
            return self._perform_async_post(content, syntax)
        return self._perform_sync_post(content, syntax)

    def _perform_sync_post(self, content: str, syntax: str = None) -> Paste:
        assert not isinstance(self.session, aiohttp.ClientSession)

        payload = {"meta": [{"index": 0, "syntax": syntax}]}

        assert self.session is not None and not isinstance(self.session, aiohttp.ClientSession)

        response: requests.Response = self.session.post(
            API_BASE_URL,
            files={
                "data": content,
                "meta": (None, json.dumps(payload), "application/json"),
            },
            timeout=CLIENT_TIMEOUT,
        )

        if response.status_code not in [200, 201]:
            raise APIError(response.status_code, response.text)

        return Paste(response.json(), syntax)

    async def _perform_async_post(self, content: str, syntax: str = None) -> Paste:
        if not self.session and self._are_we_async:
            await self._generate_async_session()

        assert self.session is not None and isinstance(self.session, aiohttp.ClientSession)

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

            if status_code != 200:
                raise APIError(status_code, response_text)

            response_data = await response.json()

        return Paste(response_data, syntax)

    def get(self, paste_id: str) -> Union[PasteData, Coroutine[None, None, PasteData]]:
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

        if not self._are_we_async:
            return self._perform_sync_get(paste_id)

        return self._perform_async_get(paste_id)

    def _perform_sync_get(self, paste_id: str) -> PasteData:
        assert self.session is not None and not isinstance(self.session, aiohttp.ClientSession)

        with self.session.get(f"{API_BASE_URL}/{paste_id}", timeout=CLIENT_TIMEOUT) as response:
            if response.status_code not in (200,):
                raise BadPasteID("This is an invalid Mystb.in paste ID.")

        paste_data = response.json()
        return PasteData(paste_id, paste_data)

    async def _perform_async_get(self, paste_id: str) -> PasteData:
        if not self.session:
            await self._generate_async_session()

        assert self.session is not None and isinstance(self.session, aiohttp.ClientSession)

        async with self.session.get(f"{API_BASE_URL}/{paste_id}", timeout=aiohttp.ClientTimeout(CLIENT_TIMEOUT)) as response:
            if response.status not in (200,):
                raise BadPasteID("This is an invalid Mystb.in paste ID.")
            paste_data = await response.json()

        return PasteData(paste_id, paste_data)

    async def close(self) -> None:
        """Async only - close the session."""
        if self.session and isinstance(self.session, aiohttp.ClientSession):
            await self.session.close()
