import asyncio
from logging import getLogger
from os import name
from asyncio import new_event_loop as new_asyncio_loop

from uvloop import new_event_loop as new_uvloop_loop, install as uvloop_install

from netnet.structure.common import Bot, setup_logger

setup_logger()
_log = getLogger(__name__)

if name != 'nt':
    uvloop_install()
    loop = new_uvloop_loop()
    _log.info('Installed uvloop')
else:
    loop = new_asyncio_loop()
    _log.info('Use basic asyncio')

if __name__ == '__main__':
    _log.debug('Starting...')
    bot = Bot(loop=loop)
    bot.please_run()
