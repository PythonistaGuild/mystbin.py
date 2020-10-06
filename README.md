# Mystb.in-py!

A small simple wrapper around the [Mystb.in](https://mystb.in/) API.

### Features

- [x] - `POST`ing to the API, which will return the provided url.
- [x] - `GET`ting from the API, provided you know the URL or paste ID.
- [x] - Ability to pass in a sync or async session / parameter so it is flexible.
- [x] - Write a real underlying Client for this, it will be required for...
- [ ] - ... Authorization. Awaiting the API making this public as it is still WIP.

### Installation
This project will be on [PyPI](https://pypi.org/project/mystbin.py/) as a stable release, you can always find that there.

Installing via `pip`:
```shell
python -m pip install -U mystbin.py
# or for optional sync addon...
python -m pip install -U mystbin.py[requests]
```

Installing from source:
```shell
python -m pip install git+https://github.com/AbstractUmbra/mystbin-py.git #[requests] for sync addon
```

### Usage examples
Since the project is considered multi-sync, it will work in a sync/async environment, see the optional dependency of `requests` below.

```py
# async example - it will default to async
import mystbin

mystbin_client = mystbin.MystbinClient() ## api_key kwarg for authentication also

paste = await mystbin_client.post("Hello from Mystb.in!", syntax="python")
str(paste)
>>> 'https://mystb.in/<your generated ID>.python'

paste.url
>>> 'https://mystb.in/<your generated ID>.python'

get_paste = await mystbin_client.get("https://mystb.in/<your generated ID>")
str(paste)
>>> "Hello from Mystb.in!"

paste.created_at
>>> datetime.datetime(2020, 10, 6, 10, 53, 57, 556741)
```

```py
# sync example - we need to pass a session though
import mystbin
import requests

sync_session = requests.Session()
mystbin_client = mystbin.MystbinClient(session=sync_session) ## optional api_key kwarg also

mystbin_client.post("Hello from sync Mystb.in!", syntax="text")
>>> 'https://mystb.in/<your generated ID>.text'
```

NOTE: the session - aiohttp or requests - will have their default headers changed during init to support the Authorization header with the api key if present, and there is a timeout of 15s for each operation.

### Dependencies

`aiohttp` - required \
`requests` - optional