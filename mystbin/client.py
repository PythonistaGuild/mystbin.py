"""
The MIT License (MIT)

Copyright (c) 2020 AbstractUmbra

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
from typing import TYPE_CHECKING, Awaitable, Optional, Union

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
    api_key: Optional[:class:`str`]
        Your private API token to access the Mystb.in API.
        Currently unobtainable.
    session: Optional[Union[:class:`aiohttp.ClientSession`, :class:`requests.Session`]]
        Optional session to be passed to the creation of the client.
    """

    __slots__ = ("api_key", "session", "_are_we_async")

    def __init__(
        self,
        *,
        api_key: str = None,
        session: Optional[Union[aiohttp.ClientSession, requests.Session]] = None,
    ) -> None:
        self.api_key = api_key
        self._are_we_async = session is None or isinstance(
            session, aiohttp.ClientSession
        )
        self.session = (
            self._generate_sync_session(session) if not self._are_we_async else None
        )

    def _generate_sync_session(self, session: requests.Session) -> requests.Session:
        """ We will update a :class:`requests.Session` instance with the auth we require. """
        # the passed session was found to be 'sync'.
        if self.api_key:
            session.headers.update(
                {"Authorization": self.api_key, "User-Agent": "Mystbin.py"}
            )

        return session

    async def _generate_async_session(
        self, session: Optional[aiohttp.ClientSession] = None
    ) -> aiohttp.ClientSession:
        """ We will update (or create) a :class:`aiohttp.ClientSession` instance with the auth we require. """
        if not session:
            session = aiohttp.ClientSession(raise_for_status=False)

        if self.api_key:
            session._default_headers.update(
                {"Authorization": self.api_key, "User-Agent": "Mystbin.py"}
            )

        session._timeout = aiohttp.ClientTimeout(CLIENT_TIMEOUT)
        return session

    def post(self, content: str, syntax: str = None) -> Union[Paste, Awaitable]:
        """
        This will post to the Mystb.in API and return the url.
        Can pass an optional suffix for the syntax highlighting.

        Parameters
        ----------
        content: :class:`str`
            The content you are posting to the Mystb.in API.
        syntax: :class:`str`
            The optional suffix to append the returned URL which is used for syntax highlighting on the paste.
        """
        if self._are_we_async:
            return self._perform_async_post(content, syntax)
        return self._perform_sync_post(content, syntax)

    def _perform_sync_post(self, content: str, syntax: str = None) -> Paste:
        """ Sync post request. """
        payload = {"meta": [{"index": 0, "syntax": syntax}]}
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
        """ Async post request. """
        if not self.session and self._are_we_async:
            self.session = await self._generate_async_session()

        multi_part_write = aiohttp.MultipartWriter()
        paste_content = multi_part_write.append(content)
        paste_content.set_content_disposition("form-data", name="data")
        paste_content = multi_part_write.append_json(
            {"meta": [{"index": 0, "syntax": syntax}]}
        )
        paste_content.set_content_disposition("form-data", name="meta")

        async with self.session.post(API_BASE_URL, data=multi_part_write) as response:
            status_code = response.status
            response_text = await response.text()
            if status_code not in (200,):
                raise APIError(status_code, response_text)
            response_data = await response.json()

        return Paste(response_data, syntax)

    def get(self, paste_id: str) -> Union[PasteData, Awaitable]:
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
        syntax = paste_id_match.group("syntax")

        if not self._are_we_async:
            return self._perform_sync_get(paste_id, syntax)

        return self._perform_async_get(paste_id, syntax)

    def _perform_sync_get(self, paste_id: str, syntax: str = None) -> PasteData:
        """ Sync get request. """
        response: requests.Response = self.session.get(
            f"{API_BASE_URL}/{paste_id}", timeout=CLIENT_TIMEOUT
        )

        if response.status_code not in (200,):
            raise BadPasteID("This is an invalid Mystb.in paste ID.")

        paste_data = response.json()
        return PasteData(paste_id, paste_data)

    async def _perform_async_get(self, paste_id: str, syntax: str = None) -> PasteData:
        """ Async get request. """
        if not self.session:
            self.session: aiohttp.ClientSession = await self._generate_async_session()

        async with self.session.get(
            f"{API_BASE_URL}/{paste_id}", timeout=aiohttp.ClientTimeout(CLIENT_TIMEOUT)
        ) as response:
            if response.status not in (200,):
                raise BadPasteID("This is an invalid Mystb.in paste ID.")
            paste_data = await response.json()

        return PasteData(paste_id, paste_data)

    async def close(self):
        """ Async only - close the session. """
        if self.session and isinstance(self.session, aiohttp.ClientSession):
            await self.session.close()
