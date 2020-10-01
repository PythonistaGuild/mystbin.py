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
import re

import aiohttp

BASE = "https://mystb.in/api/pastes"
# Let's set aiohttp timeout for this
TIMEOUT = aiohttp.ClientTimeout(total=15.0)

# grab the paste id: https://regex101.com/r/qkluDh/1
MB_URL_RE = re.compile(r"(?:http[s]?://mystb\.in/)?([a-zA-Z]+)(?:.*)")

async def post(content: str, *, session: aiohttp.ClientSession = None, suffix: str = None) -> str:
    """ Post `content` to MystB.in with optional suffix text. """
    suffix = f".{suffix}" if suffix else ""
    multi_part = aiohttp.MultipartWriter()
    paste_content = multi_part.append(content)
    paste_content.set_content_disposition("form-data", name="data")
    paste_content = multi_part.append_json({"meta": [{"index": 0, "syntax": suffix}]})
    paste_content.set_content_disposition("form-data", name="meta")
    session = session or aiohttp.ClientSession(raise_for_status=True)
    async with session.post(BASE, data=multi_part, timeout=TIMEOUT) as mb_res:
        url = await mb_res.json()
    short_id = url['pastes'][0]['id']
    return f"https://mystb.in/{short_id}{suffix}"

async def get(paste: str, *, session: aiohttp.ClientSession = None) -> dict:
    try:
        paste_id = MB_URL_RE.match(paste)[1]
    except IndexError:
        return "This is not a valid Mystb.in paste ID or URL."
    session = session or aiohttp.ClientSession(raise_for_status=True)
    async with session.get(f"{BASE}/{paste_id}", timeout=TIMEOUT) as mb_res:
        data_json = await mb_res.json()
    return data_json
