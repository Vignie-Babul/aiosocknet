import asyncio
import contextlib
import logging
from logging.config import fileConfig

from aiosocknet import (
	AIOSockServ,
	AIOSockConn,
	HTTPStatus,
	JSONResponse,
	APIRouter,
)


fileConfig('logging.ini')
_log = logging.getLogger(__name__)


distros = [
	'Arch Linux', 'CachyOS',
	'Debian', 'Fedora',
	'Gentoo', 'Linux Mint',
	'NixOS', 'Ubuntu',
]


router = APIRouter()


@router.route('/')
def root() -> JSONResponse:
	return JSONResponse(
		HTTPStatus.OK,
		{'response': 'Hello, Python WebServer!'},
	)


@router.route('/distros/{distro_id}')
def get_distro(distro_id: str) -> JSONResponse:
	distro_id: int = min(int(distro_id), len(distros) - 1)
	return JSONResponse(
		HTTPStatus.OK,
		{
			str(distro_id): distros[distro_id]
		},
	)


@router.route('/tux')
def get_tux_info() -> JSONResponse:
	return JSONResponse(HTTPStatus.OK, {
		'name': 'Tux',
		'birth_date': [9, 5, 1996],
		'company': {
			'name': 'Linux',
			'website': 'https://www.linux.org/',
		},
	})


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
