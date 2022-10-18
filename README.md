<div align="center">
    <h1>Mystbin.py!</h1>
    <a href='https://mystbinpy.readthedocs.io/en/latest/?badge=latest'>
        <img src='https://readthedocs.org/projects/mystbinpy/badge/?version=latest' alt='Documentation Status' />
    </a>
    <a href='https://github.com/PythonistaGuild/mystbin.py/workflows/Code%20Linting'>
        <img src='https://github.com/PythonistaGuild/mystbin.py/workflows/Code%20Linting/badge.svg?branch=main' alt='Linting status' />
    </a>
    <a href='https://github.com/PythonistaGuild/mystbin.py/workflows/Build'>
        <img src='https://github.com/PythonistaGuild/mystbin.py/workflows/Build/badge.svg' alt='Build status' />
    </a>
</div>
<br>

A small simple wrapper around the [Mystb.in](https://mystb.in/) API. API docs can be found [here](https://api.mystb.in/docs).

Documentation for this wrapper can be found [here](https://mystbinpy.readthedocs.io/en/stable/).
If you want the docs for the `main` branch, those can be found [here](https://mystbinpy.readthedocs.io/en/latest/).

----------
### Features

- [x] - Creating pastes.
- [ ] - Editing pastes.
    - Pending design work.
- [x] - Deleting pastes.
- [x] - Getting pastes.
- [ ] - User endpoints.
- [ ] - Sync client.
  - This one will take some time as I have no motivation to do it, but PRs are welcome if others want to do it.

### Installation
This project will be on [PyPI](https://pypi.org/project/mystbin.py/) as a stable release, you can always find that there.

Installing via `pip`:
```shell
python -m pip install -U mystbin.py
```

Installing from source:
```shell
python -m pip install git+https://github.com/PythonistaGuild/mystbin.py.git
```

### Usage examples
Since the project is considered multi-sync, it will work in a sync/async environment, see the optional dependency of `requests` below.

```py
# async example - it will default to async
import mystbin

mystbin_client = mystbin.Client()

paste = await client.create_paste(filename="Hello.txt", content="Hello there!")
str(paste)
>>> 'https://mystb.in/<your generated ID>'

get_paste = await mystbin_client.get_paste("<your generated ID>")
get_paste.files[0].content
>>> "Hello there!"

get_paste.created_at
>>> datetime.datetime(2020, 10, 6, 10, 53, 57, 556741)
```

Or if you want to create a paste with multiple files...
```py
import mystbin

file = mystbin.File(filename="File1.txt", content="Hello there!")
file2 = mystbin.File(filename="test.py", content="print('hello!')")

paste = await client.create_multifile_paste(files=[file, file2])

for file in paste.files:
    print(file.content)

>>> "Hello there!"
>>> "print('hello!')"
```

If you have any question please feel free to join the Pythonista Discord server:
<div align="left">
    <a href="https://discord.gg/RAKc3HF">
        <img src="https://discordapp.com/api/guilds/490948346773635102/widget.png?style=banner2" alt="Discord Server"/>
    </a>
</div>
