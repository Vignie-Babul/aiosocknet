import asyncio
import contextlib
import logging
from logging.config import fileConfig

from aiosocknet import AIOSockServ, AIOSockConn


fileConfig('logging.ini')
_log = logging.getLogger(__name__)


async def handle_client(conn: AIOSockConn) -> None:
	request = await conn.recv()
	if request is None:
		return
	_log.debug(request)
	await conn.send('HTTP/1.1 200 OK\r\nContent-Length: 8\r\nConnection: close\r\n\r\nresponse')


async def main(host: str, port: int) -> None:
	async with AIOSockServ(host, port) as serv:
		while True:
			conn = await serv.accept()
			async with conn(handle_client): ...

			# async with conn:
			# 	await asyncio.create_task(handle_client(conn))


if __name__ == '__main__':
	with contextlib.suppress(KeyboardInterrupt):
		asyncio.run(main('127.0.0.1', 65535))
