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
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Sequence

    from typing_extensions import Self

    from .http import HTTPClient
    from .types.responses import CreatePasteResponse, FileResponse, GetPasteResponse


__all__ = (
    "File",
    "Paste",
)


class File:
    _lines_of_code: int
    _character_count: int
    _parent_id: str
    _annotation: str

    """Represents a single file within a mystb.in paste.

    Attributes
    -----------
    filename: :class:`str`
        The file's name.
    content: :class:`str`
        The file's contents.
    """

    __slots__ = (
        "_annotation",
        "_character_count",
        "_lines_of_code",
        "_parent_id",
        "content",
        "filename",
    )

    def __init__(self, *, filename: str, content: str) -> None:
        self.filename: str = filename
        self.content: str = content

    @property
    def lines_of_code(self) -> int:
        return self._lines_of_code

    @property
    def character_count(self) -> int:
        return self._character_count

    @property
    def annotation(self) -> str:
        return self._annotation

    @property
    def parent_id(self) -> str:
        return self._parent_id

    @classmethod
    def from_data(cls, payload: FileResponse, /) -> Self:
        self = cls(
            content=payload["content"],
            filename=payload["filename"],
        )
        self._lines_of_code = payload["loc"]
        self._character_count = payload["charcount"]
        self._annotation = payload["annotation"]
        self._parent_id = payload["parent_id"]

        return self

    def to_dict(self) -> dict[str, Any]:
        return {"content": self.content, "filename": self.filename}


class Paste:
    _expires: datetime.datetime | None
    _views: int | None
    _security: str | None

    """Represents a Paste object from mystbin instances.

    Attributes
    -----------
    id: :class:`str`
        The ID of this paste.
    created_at: :class:`datetime.datetime`
        When this paste was created in UTC.
    files: List[:class:`mystbin.File`]
        The list of files within this Paste.
    """

    __slots__ = (
        "_expires",
        "_http",
        "_security",
        "_views",
        "author_id",
        "created_at",
        "files",
        "id",
    )

    def __init__(self, *, http: HTTPClient, paste_id: str, created_at: str, files: Sequence[File]) -> None:
        self._http: HTTPClient = http
        self.id: str = paste_id
        self.created_at: datetime.datetime = datetime.datetime.fromisoformat(created_at)
        self.files: Sequence[File] = files

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f"<Paste id={self.id!r} files={len(self.files)}>"

    @property
    def url(self) -> str:
        return f"{self._http.api_base}{self.id}"

    @property
    def expires(self) -> datetime.datetime | None:
        return self._expires

    @property
    def views(self) -> int | None:
        return self._views

    @property
    def security_token(self) -> str | None:
        return self._security

    @classmethod
    def from_get(cls, payload: GetPasteResponse, /, *, http: HTTPClient) -> Self:
        files = [File.from_data(data) for data in payload["files"]]
        self = cls(
            http=http,
            paste_id=payload["id"],
            created_at=payload["created_at"],
            files=files,
        )
        self._views = payload["views"]

        expires = payload["expires"]
        if expires:
            self._expires = datetime.datetime.fromisoformat(expires)
        else:
            self._expires = None

        self._security = None

        return self

    @classmethod
    def from_create(cls, payload: CreatePasteResponse, files: Sequence[File], *, http: HTTPClient) -> Self:
        self = cls(
            http=http,
            paste_id=payload["id"],
            created_at=payload["created_at"],
            files=files,
        )
        self._views = 0

        expires = payload["expires"]
        if expires:
            self._expires = datetime.datetime.fromisoformat(expires)
        else:
            self._expires = None

        self._security = payload["safety"]

        return self

    async def delete(self) -> None:
        if not self.security_token:
            raise ValueError("Cannot delete a Paste with no Security Token set.")

        await self._http.delete_paste(self.security_token)
