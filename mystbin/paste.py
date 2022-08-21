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
from typing import TYPE_CHECKING, Any, Optional


if TYPE_CHECKING:
    from typing_extensions import Self

    from mystbin.types.responses import FileResponse, PasteResponse

__all__ = (
    "File",
    "Paste",
)


class File:
    """Represents a single file within a mystb.in paste.

    Attributes
    -----------
    filename: :class:`str`
        The file's name.
    content: :class:`str`
        The file's contents.
    syntax: Optional[:class:`str`]
        The file's syntax, if given.
    lines_of_code: Optional[:class:`int`]
        The lines of code within the file.
    character_count: Optional[:class:`int`]
        The character count of the file.


    .. note::
        The ``lines_of_code`` and ``character_count`` come from the API and should not be provided by the user.
    """

    __slots__ = (
        "filename",
        "content",
        "syntax",
        "lines_of_code",
        "character_count",
    )

    def __init__(
        self,
        *,
        filename: str,
        content: str,
        syntax: Optional[str],
        lines_of_code: Optional[int] = None,
        character_count: Optional[int] = None,
    ) -> None:
        self.filename: str = filename
        self.content: str = content
        self.syntax: Optional[str] = syntax
        self.lines_of_code: int = lines_of_code or content.count("\n")
        self.character_count: int = character_count or len(content)

    @classmethod
    def _from_data(cls, payload: FileResponse, /) -> Self:
        return cls(
            content=payload["content"],
            filename=payload["filename"],
            syntax=payload["filename"].rsplit(".")[-1],
            lines_of_code=payload["loc"],
            character_count=payload["charcount"],
        )

    def _to_dict(self) -> dict[str, Any]:
        ret: dict[str, Any] = {"content": self.content, "filename": self.filename, "syntax": self.syntax}

        return ret


class Paste:
    """Represents a Paste object from mystb.in.

    Attributes
    -----------
    id: :class:`str`
        The ID of this paste.
    created_at: :class:`datetime.datetime`
        When this paste was created in UTC.
    expires: Optional[:class:`datetime.datetime`]
        When this paste expires, if at all.
    last_edited: Optional[:class:`datetime.datetime`]
        When this paste was last edited, if at all.
    files: list[:class:`mystbin.File`]
        The list of files within this Paste.
    views: Optional[:class:`int`]
        How many views this paste has had, if any.


    .. note::
        The ``last_edited``, ``expires`` and ``views`` attributes come from the API and are not user provided.
    """

    __slots__ = (
        "id",
        "author_id",
        "created_at",
        "expires",
        "files",
        "notice",
        "views",
        "last_edited",
    )

    def __init__(
        self,
        *,
        id: str,
        created_at: str,
        expires: Optional[str] = None,
        last_edited: Optional[str] = None,
        files: list[File],
        views: Optional[int] = None,
    ) -> None:
        self.id: str = id
        self.created_at: datetime.datetime = datetime.datetime.fromisoformat(created_at)
        self.expires: Optional[datetime.datetime] = datetime.datetime.fromisoformat(expires) if expires else None
        self.last_edited: Optional[datetime.datetime] = datetime.datetime.fromisoformat(last_edited) if last_edited else None
        self.files: list[File] = files
        self.views: Optional[int] = views

    def __str__(self) -> str:
        return f"https://mystb.in/{self.id}"

    def __repr__(self) -> str:
        return f"<Paste id={self.id!r} files={len(self.files)}>"

    @classmethod
    def _from_data(cls, payload: PasteResponse, /) -> Self:
        files = [File._from_data(data) for data in payload["files"]]
        return cls(
            id=payload["id"],
            created_at=payload["created_at"],
            expires=payload["expires"],
            files=files,
            views=payload.get("views"),
            last_edited=payload.get("last_edited"),
        )
