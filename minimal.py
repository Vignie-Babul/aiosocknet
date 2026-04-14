import asyncio
from aiosocknet import AIOSockServ, HTTPStatus, JSONResponse


async def handle_client(conn) -> None:
	request = await conn.recv()
	print(f'Received request:\n{request}') # request handling
	await conn.send(JSONResponse(
		HTTPStatus.OK,
		{'message': 'install archlinux'},
		headers={'ImportantMessage': 'I use Arch btw'},
	))


async def main(host: str, port: int) -> None:
	async with AIOSockServ(host, port) as serv:
		while True:
			conn = await serv.accept()
			async with conn(handle_client): ...


if __name__ == '__main__':
	asyncio.run(main('127.0.0.1', 65535))
