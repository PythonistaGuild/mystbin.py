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
from typing import TYPE_CHECKING, Any, Dict, List, Optional


if TYPE_CHECKING:
    from typing_extensions import Self

    from mystbin.types.responses import FileResponse, PasteResponse

__all__ = (
    "File",
    "Paste",
)


class File:
    _lines_of_code: int
    _character_count: int

    """Represents a single file within a mystb.in paste.

    Attributes
    -----------
    filename: :class:`str`
        The file's name.
    content: :class:`str`
        The file's contents.
    """

    __slots__ = (
        "filename",
        "content",
        "attachment_url",
        "_lines_of_code",
        "_character_count",
    )

    def __init__(self, *, filename: str, content: str, attachment_url: Optional[str] = None) -> None:
        self.filename: str = filename
        self.content: str = content
        self.attachment_url: Optional[str] = attachment_url

    @property
    def lines_of_code(self) -> int:
        return self._lines_of_code

    @property
    def character_count(self) -> int:
        return self._character_count

    @classmethod
    def from_data(cls, payload: FileResponse, /) -> Self:
        self = cls(content=payload["content"], filename=payload["filename"], attachment_url=payload["attachment"])
        self._lines_of_code = payload["loc"]
        self._character_count = payload["charcount"]

        return self

    def to_dict(self) -> Dict[str, Any]:
        ret: Dict[str, Any] = {"content": self.content, "filename": self.filename}

        return ret


class Paste:
    _last_edited: Optional[datetime.datetime]
    _expires: Optional[datetime.datetime]
    _views: Optional[int]

    """Represents a Paste object from mystb.in.

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
        "id",
        "author_id",
        "created_at",
        "files",
        "notice",
        "_expires",
        "_views",
        "_last_edited",
    )

    def __init__(self, *, id: str, created_at: str, files: List[File], notice: Optional[str]) -> None:
        self.id: str = id
        self.created_at: datetime.datetime = datetime.datetime.fromisoformat(created_at)
        self.files: List[File] = files
        self.notice: Optional[str] = notice

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f"<Paste id={self.id!r} files={len(self.files)}>"

    @property
    def url(self) -> str:
        return f"https://mystb.in/{self.id}"

    @property
    def last_edited(self) -> Optional[datetime.datetime]:
        return self._last_edited

    @property
    def expires(self) -> Optional[datetime.datetime]:
        return self._expires

    @property
    def views(self) -> Optional[int]:
        return self._views

    @classmethod
    def from_data(cls, payload: PasteResponse, /) -> Self:
        files = [File.from_data(data) for data in payload["files"]]
        self = cls(id=payload["id"], created_at=payload["created_at"], files=files, notice=payload["notice"])
        self._views = payload.get("views")
        last_edited = payload.get("last_edited")
        if last_edited:
            self._last_edited = datetime.datetime.fromisoformat(last_edited)
        else:
            self._last_edited = None

        expires = payload["expires"]
        if expires:
            self._expires = datetime.datetime.fromisoformat(expires)
        else:
            self._expires = None

        return self
