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

import datetime
from textwrap import dedent

from .constants import PASTE_BASE


class Paste:
    """
    A class representing the return data from the API after performing a POST request.

    Attributes
    ----------
    paste_id: :class:`str`
        The ID returned from the API. Genertally it is 3 random choice English words.
    nick: :class:`str`
        The nickname you requested the paste be named.
    syntax: :class:`str`
        The syntax (or syntax highlighting) you requested when creating the Paste. Returns as a suffix on the URL.
    """

    __slots__ = ("paste_id", "nick", "syntax")

    def __init__(self, json_data: dict, syntax: str = None):
        self.paste_id = json_data["pastes"][0]["id"]
        self.nick = json_data["pastes"][0]["nick"]
        self.syntax = syntax

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return f"<Paste id={self.paste_id} nick={self.nick} syntax={self.syntax}>"

    @property
    def url(self) -> str:
        """ :class:`str`: Returns the formatted url of ID and syntax. """
        syntax = f".{self.syntax}" if self.syntax else ""
        return PASTE_BASE.format(self.paste_id, syntax)

    def with_syntax(self, new_syntax: str) -> str:
        """
        Changes the syntax of the current Paste to `new_syntax`

        Parameters
        ----------
        new_syntax: :class:`str`
            The new suffix to append to the Paste.
        """
        new_syntax = f".{new_syntax}" if new_syntax else None
        return PASTE_BASE.format(self.paste_id, new_syntax)


class PasteData:
    """
    A class representing the return data from the API after performing a GET request.

    Attributes
    ----------
    paste_id: :class:`str`
        The ID you wish to retrieve from the API.
    paste_content: :class:`str`
        The content returned from the paste.
    paste_syntax: :class:`str`
        The syntax you specified that this Paste is in.
    paste_nick: :class:`str`
        The nick set for this paste on the API.
    paste_date: :class:`datetime.datetime`
        The date this paste was created on the API.
    """

    __slots__ = (
        "paste_id",
        "_paste_data",
        "paste_content",
        "paste_syntax",
        "paste_nick",
        "paste_date",
    )

    def __init__(self, paste_id: str, paste_data: dict):
        self.paste_id = paste_id
        self._paste_data = paste_data
        self.paste_content = paste_data["data"]
        self.paste_syntax = paste_data["syntax"]
        self.paste_nick = paste_data["nick"]
        self.paste_date = paste_data["created_at"]

    def __str__(self) -> str:
        return self.content

    def __repr__(self) -> str:
        return f"<PasteData id={self.paste_id} nick={self.paste_nick} syntax={self.paste_syntax}>"

    @property
    def url(self) -> str:
        """ :class:`str`: The Paste ID's URL """
        syntax = f".{self.paste_syntax}" if self.paste_syntax else ""
        return PASTE_BASE.format(self.paste_id, syntax)

    @property
    def created_at(self) -> datetime.datetime:
        """ :class:`datetime.datetime`: Returns a UTC datetime of when the paste was created. """
        return datetime.datetime.strptime(self.paste_date, "%Y-%m-%dT%H:%M:%S.%f")

    @property
    def content(self) -> str:
        """ :class:`str`: Return the paste content but dedented correctly. """
        return dedent(self.paste_content)
