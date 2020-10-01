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

from typing import Optional, Union

import aiohttp
import yarl

from .constants import *
from .errors import *

__all__ = ("MystClient", )

class MystClient():
    """
    Client for interacting with the Mystb.in API.

    Attributes
    ----------
    authorization: Optional[:class:`dict`]
                Your username | password combination to access the Mystb.in API.
                Can be obtained via: #TODO
    api_key: Optional[:class:`str`]
                Your private API token to access the Mystb.in API.
                Can be obtained via: #TODO
    session: Optional[Union[:class:`ClientSession`, :class:`Session`]]
    """
    __slots__ = ("authorization", "api_key", "session")

    def __init__(
        self,
        authorization: dict = None,
        api_key: str = None, *,
        session: Optional[Union[aiohttp.ClientSession, requests.Session]] = None,
    )