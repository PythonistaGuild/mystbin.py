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
    __slots__ = ("paste_id", "nick", "syntax")
    def __init__(self, json_data: dict, syntax: str = None) -> None:
        self.paste_id = json_data['pastes'][0]['id']
        self.nick = json_data['pastes'][0]['nick']
        self.syntax = syntax

    def __str__(self) -> str:
        """ Cast the Paste to a string for the URL. """
        return self.url

    def __repr__(self) -> str:
        """ Paste repr. """
        return f"<Paste id={self.paste_id} nick={self.nick} syntax={self.syntax}>"

    @property
    def url(self) -> str:
        syntax = f".{self.syntax}" if self.syntax else ""
        return PASTE_BASE.format(self.paste_id, syntax)
    
    def with_syntax(self, new_syntax: str) -> str:
        return PASTE_BASE.format(self.paste_id, new_syntax)

class PasteData:
    __slots__ = ("paste_id", "_paste_data", "paste_content", "paste_syntax", "paste_nick", "paste_date")
    def __init__(self, paste_id: str, paste_data: dict) -> None:
        self.paste_id = paste_id
        self._paste_data = paste_data
        self.paste_content = paste_data['data']
        self.paste_syntax = paste_data['syntax']
        self.paste_nick = paste_data['nick']
        self.paste_date = paste_data['created_at']

    def __str__(self) -> str:
        """ We'll return the paste content. Since it's dev stuff, dedent it. """
        return self.content

    def __repr__(self) -> str:
        """ Paste content repr. """
        return f"<PasteData id={self.paste_id} nick={self.paste_nick} syntax={self.paste_syntax}>"

    @property
    def url(self) -> str:
        """ The Paste ID's URL """
        syntax = f".{self.paste_syntax}" if self.paste_syntax else ""
        return PASTE_BASE.format(self.paste_id, syntax)

    @property
    def created_at(self) -> datetime.datetime:
        """ Returns a UTC datetime of when the paste was created. """
        return datetime.datetime.strptime(self.paste_date, "%Y-%m-%dT%H:%M:%S.%f")

    @property
    def content(self) -> str:
        """ Return the paste content but dedented correctly. """
        return dedent(self.paste_content)
