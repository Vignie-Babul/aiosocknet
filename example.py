import asyncio
import contextlib
import logging
from logging.config import fileConfig

from aiosocknet import (
	AIOSockServ,
	AIOSockConn,
	HTTPStatus,
	JSONResponse,
	Router,
)


fileConfig('logging.ini')
_log = logging.getLogger(__name__)


distros = [
	'Arch Linux', 'CachyOS',
	'Debian', 'Fedora',
	'Gentoo', 'Linux Mint',
	'NixOS', 'Ubuntu',
]


router = Router()


@router.route('/')
def root() -> JSONResponse:
	return JSONResponse(
		HTTPStatus.OK,
		{'response': 'Python WebServer with aiosocknet!'},
	)


@router.route('/distros/{distro_id}')
def get_distro(distro_id: str) -> JSONResponse:
	return JSONResponse(
		HTTPStatus.OK,
		{
			distro_id: distros[int(distro_id)]
		},
	)


async def handle_client(conn: AIOSockConn) -> None:
	request = await conn.recv()
	if request is None:
		return
	_log.debug(request)

	await conn.send(
		router.get(request)
	)


async def main(host: str, port: int) -> None:
	async with AIOSockServ(host, port) as serv:
		while True:
			conn = await serv.accept()
			async with conn(handle_client): ...


if __name__ == '__main__':
	with contextlib.suppress(KeyboardInterrupt):
		asyncio.run(main('127.0.0.1', 65535))
