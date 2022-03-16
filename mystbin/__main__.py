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

import argparse
import platform
import sys

import aiohttp
import pkg_resources


try:
    import requests
except ImportError:
    requests = None

import mystbin


def show_version() -> None:
    entries: list[str] = []

    entries.append("- Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(sys.version_info))
    version_info = mystbin.version_info
    entries.append("- mystbin.py v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}".format(version_info))

    if version_info.releaselevel != "final":
        pkg = pkg_resources.get_distribution("mystbin.py")
        if pkg:
            entries.append("    - mystbin.py pkg_resources: v{0}".format(pkg.version))

    entries.append("- aiohttp v{0.__version__}".format(aiohttp))

    if requests is not None:
        entries.append("  - [requests] v{0.__version__}".format(requests))

    uname = platform.uname()
    entries.append("- system info: {0.system} {0.release} {0.version}".format(uname))

    print("\n".join(entries))


def parse_args() -> tuple[argparse.ArgumentParser, argparse.Namespace]:
    parser = argparse.ArgumentParser(prog="mystbin", description="Tools for helping with mystbin.py")
    parser.add_argument("-v", "--version", action="store_true", help="shows the wrapper version")
    parser.set_defaults(func=core)

    return parser, parser.parse_args()


def core(_: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.version:
        show_version()


def main() -> None:
    parser, args = parse_args()
    args.func(parser, args)


main()
