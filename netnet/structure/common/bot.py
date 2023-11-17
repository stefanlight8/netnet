import importlib.util
import importlib.machinery
import os
import pkgutil
import sys
import types
from logging import getLogger
from os import getenv
from asyncio import AbstractEventLoop

from aiohttp import ClientSession
from quant import Client, Intents
from quant.events import ReadyEvent
from uvloop import Loop
from dotenv import load_dotenv

from netnet.structure.api import KawaiiAPI

load_dotenv(override=True)
_log = getLogger(__name__)


def is_submodule(parent: str, child: str) -> bool:
    return parent == child or child.startswith(parent + ".")


def call_module_finalizers(self, lib: types.ModuleType, key: str) -> None:
    try:
        func = lib.teardown
    except AttributeError:
        pass
    else:
        try:
            func(self)
        except Exception as error:
            error.__suppress_context__ = True
            _log.error("Exception in extension finalizer %r", key, exc_info=error)
    finally:
        self.plugins.pop(key, None)
        sys.modules.pop(key, None)
        name = lib.__name__
        for module in list(sys.modules.keys()):
            if is_submodule(name, module):
                del sys.modules[module]


def search_directory(directory: str) -> list[str]:
    relpath = os.path.relpath(directory)
    if ".." in relpath:
        raise ValueError("Modules outside the cwd require a package to be specified")
    abspath = os.path.abspath(directory)
    if not os.path.exists(relpath):
        raise ValueError(f"Provided path '{abspath}' does not exist")
    if not os.path.isdir(relpath):
        raise ValueError(f"Provided path '{abspath}' is not a directory")
    prefix = relpath.replace(os.sep, ".")
    if prefix in ("", "."):
        prefix = ""
    else:
        prefix += "."
    for _, name, is_package in pkgutil.iter_modules([directory]):
        if is_package:
            yield from search_directory(os.path.join(directory, name))
        else:
            yield prefix + name


async def load_from_module_spec(self, spec: importlib.machinery.ModuleSpec, key: str) -> None:
    lib = importlib.util.module_from_spec(spec)
    sys.modules[key] = lib
    try:
        spec.loader.exec_module(lib)
    except Exception as e:
        del sys.modules[key]
        raise TypeError(f"Failed to load {key}:\n{e}") from e
    try:
        setup = lib.setup
    except AttributeError:
        del sys.modules[key]
        raise TypeError(f"Setup function is None {key}") from None
    try:
        await setup(self)
    except Exception as e:
        del sys.modules[key]
        self.plugins.pop(lib.__name__)
        call_module_finalizers(self, lib, key)
        raise TypeError(f"Failed to load {key}:\n{e}") from e
    else:
        self.plugins[key] = lib


class Bot(Client):
    def __init__(self, loop: AbstractEventLoop | Loop) -> None:
        self.loop = loop
        self.session: ClientSession | None = None
        self.kawaii_api: KawaiiAPI | None = None
        self.plugins: dict = {}
        super().__init__(
            token=getenv('DISCORD_TOKEN'),
            intents=Intents.ALL,
            mobile_status=True
        )

    async def on_ready(self, _: ReadyEvent):
        self.session = ClientSession(loop=self.loop)
        self.kawaii_api = KawaiiAPI(token=getenv('KAWAIIAPI_TOKEN'), session=self.session)
        await self.load_plugins('plugins')

    async def load_plugins(self, directory: str) -> None:
        for plugin in search_directory(directory):
            _log.debug(f'Loading {plugin}...')
            try:
                name = importlib.util.resolve_name(plugin, plugin)
            except ImportError as e:
                raise TypeError(f"Plugin {plugin} is not found") from e

            if name in [_plugin.keys for _plugin in self.plugins]:
                raise TypeError(f"Plugin {name} is already loaded")

            spec = importlib.util.find_spec(name)
            if spec is None:
                raise TypeError(f"Plugin {name} is not found")

            await load_from_module_spec(self, spec, name)
            _log.info(f'Loaded {name}')
            self.plugins[name] = plugin

    def please_run(self) -> None:
        _log.debug('Running...')
        self.add_listener(ReadyEvent, self.on_ready)
        super().run(self.loop)
