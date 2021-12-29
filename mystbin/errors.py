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

__all__ = (
    "BadPasteID",
    "MystbinException",
    "APIError",
)


class BadPasteID(ValueError):
    """Bad Paste ID."""


class MystbinException(Exception):
    """Error when interacting with Mystbin."""


class APIError(MystbinException):
    """
    Exception relationg to the API of Mystbin.

    Attributes
    ----------
    status_code: :class:`int`
        The HTTP Status code return from the API.
    message: :class:`str`
        The Message supplied with the HTTP status code from the API.
    """

    __slots__ = ("status_code", "message")

    def __init__(self, status_code: int, message: str):
        self.status_code: int = status_code
        self.message: str = message

    def __repr__(self) -> str:
        return f"<MystbinError status_code={self.status_code} message={self.message}>"

    def __str__(self) -> str:
        return self.message
