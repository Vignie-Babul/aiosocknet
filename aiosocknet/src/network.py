from __future__ import annotations
import asyncio
from collections.abc import Callable
import logging
import socket
from typing import Any


def empty_callable(*args: Any, **kwargs: Any) -> None: pass


class SockServ:
	def __init__(
		self,
		host: str,
		port: int,
		*,
		backlog: int = 10,
		bufsize: int = 4096,
		address_family=socket.AF_INET,  # IPv4
		socket_type=socket.SOCK_STREAM, # TCP
	) -> None:

		self._log = logging.getLogger(__name__)

		self._host = host
		self._port = port
		self._backlog = backlog
		self._bufsize = bufsize
		self._address_family = address_family
		self._socket_type = socket_type

		self._ipv4_addr = f'{host}:{port}'
		self._server_hyperlink = (
			f'\033]8;;http://{self._ipv4_addr}/\033\\http://{self._ipv4_addr}/\033]8;;\033\\\n'
		)

	def __enter__(self) -> SockServ:
		self._create_server_socket()
		return self

	def __exit__(self, exc_type, exc_val, exc_tb) -> None:
		self.close()

	def _create_server_socket(self) -> None:
		self._sock = socket.socket(self._address_family, self._socket_type)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.bind((self._host, self._port))
		self._sock.listen(self._backlog)

		self._log.info(f'Server socket is active at {self._server_hyperlink}')

	def close(self) -> None:
		try:
			self._log.info(f'Shutdown server socket {self._ipv4_addr}')
			self._sock.shutdown(socket.SHUT_RDWR)
		except OSError as e:
			self._log.error(f'Socket error occurred: {e}')	
		finally:
			self._log.info(f'Closing server socket {self._ipv4_addr}')
			self._sock.close()
			self._log.info(f'Server socket {self._ipv4_addr} is closed\n')

	def accept(self) -> SockConn:
		client, addr = self._sock.accept()
		return SockConn(client, addr, self._bufsize)


class SockConn:
	def __init__(self, sock: socket.socket, address: tuple[str, int], bufsize: int) -> None:
		self._log = logging.getLogger(__name__)

		self._sock = sock
		self._address = address
		self._bufsize = bufsize

		self._ipv4_addr = f'{address[0]}:{address[1]}'
		self._log.info(f'Connection made with {self._ipv4_addr}')

	def __enter__(self) -> SockConn:
		return self

	def __exit__(self, exc_type, exc_val, exc_tb) -> None:
		self.close()

	def close(self) -> None:
		try:
			self._log.info(f'Shutdown client socket {self._ipv4_addr}')
			self._sock.shutdown(socket.SHUT_RDWR)
		except OSError:
			self._log.error(f'OSError: Client socket {self._ipv4_addr} is already shutdown')
		finally:
			self._log.info(f'Closing client socket {self._ipv4_addr}')
			self._sock.close()
			self._log.info(f'Client socket {self._ipv4_addr} is closed\n')

	def recv(self) -> str:
		request = self._sock.recv(self._bufsize)
		return request.decode('utf-8')

	def sendall(self, response: str) -> None:
		self._sock.sendall(response.encode('utf-8'))


class AIOSockServ:
	def __init__(
		self,
		host: str,
		port: int,
		*,
		backlog: int = 10,
		bufsize: int = 4096,
		timeout: int = 10,
		address_family=socket.AF_INET,  # IPv4
		socket_type=socket.SOCK_STREAM, # TCP
	) -> None:

		self._log = logging.getLogger(__name__)

		self._host = host
		self._port = port
		self._backlog = backlog
		self._bufsize = bufsize
		self._timeout = timeout
		self._address_family = address_family
		self._socket_type = socket_type

		self._ipv4_addr = f'{host}:{port}'
		self._server_hyperlink = (
			f'\033]8;;http://{self._ipv4_addr}/\033\\http://{self._ipv4_addr}/\033]8;;\033\\\n'
		)

	async def __aenter__(self) -> AIOSockServ:
		self._create_server_socket()
		self._event_loop = asyncio.get_running_loop()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
		await self.close()

	def _create_server_socket(self) -> None:
		self._sock = socket.socket(self._address_family, self._socket_type)
		self._sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self._sock.bind((self._host, self._port))
		self._sock.listen(self._backlog)
		self._sock.setblocking(False)

		self._log.info(f'Server socket is active at {self._server_hyperlink}')

	async def close(self) -> None:
		try:
			self._log.info(f'Shutdown server socket {self._ipv4_addr}')
			self._sock.shutdown(socket.SHUT_RDWR)
		except OSError as e:
			self._log.error(f'Socket error occurred: {e}')
		finally:
			self._log.info(f'Closing server socket {self._ipv4_addr}')
			self._sock.close()
			self._log.info(f'Server socket {self._ipv4_addr} is closed\n')

	async def accept(self) -> AIOSockConn:
		client, addr = await self._event_loop.sock_accept(self._sock)
		return AIOSockConn(client, addr, self._bufsize, self._timeout)


class AIOSockConn:
	def __init__(
		self,
		sock: socket.socket,
		address: tuple[str, int],
		bufsize: int,
		timeout: int,
	) -> None:

		self._log = logging.getLogger(__name__)

		self._sock = sock
		self._address = address
		self._bufsize = bufsize
		self._timeout = timeout

		self._sock.setblocking(False)

		self._ipv4_addr = f'{address[0]}:{address[1]}'
		self._log.info(f'Connection made with {self._ipv4_addr}')

		# self._handler: Callable | None = None
		self._handler: Callable = empty_callable
		self._tasks: set[asyncio.Task] = set()

	async def __aenter__(self) -> AIOSockConn:
		self._event_loop = asyncio.get_running_loop()
		await self._create_handler_task()
		return self

	async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
		if not self._tasks:
			await self.close()

	def __call__(self, handler: Callable) -> AIOSockConn:
		self._handler = handler
		return self

	async def _create_handler_task(self) -> None:
		if (self._handler is not None) and (not self._tasks):
			async def _wrapper() -> None:
				try:
					await self._handler(self)
				except Exception as e:
					self._log.exception(e)
				finally:
					await self.close()

			task = asyncio.create_task(_wrapper())
			task.add_done_callback(self._tasks.discard)
			self._tasks.add(task)

	async def close(self) -> None:
		try:
			self._log.info(f'Shutdown client socket {self._ipv4_addr}')
			self._sock.shutdown(socket.SHUT_RDWR)
		except OSError:
			self._log.error(f'OSError: Client socket {self._ipv4_addr} is already shutdown')
		finally:
			self._log.info(f'Closing client socket {self._ipv4_addr}')
			self._sock.close()
			self._log.info(f'Client socket {self._ipv4_addr} is closed\n')

	async def recv(self, timeout: int | None = None) -> str | None:
		"""Receive binary-string request from the client socket

		Args:
			timeout:
				number of seconds to wait for receiving request.
				When value is `None`, method use timeout value
				from the `self._timeout`

		Returns:
			1. A string of recieved request
			2. `None` after request timed out
		"""

		if timeout is None:
			timeout = self._timeout

		try:
			request = await asyncio.wait_for(
				self._event_loop.sock_recv(self._sock, self._bufsize),
				timeout=timeout,
			)
		except (TimeoutError, asyncio.TimeoutError):
			self._log.error(
				f'TimeoutError: request from {self._ipv4_addr} timed out after {timeout} seconds'
			)
			return None

		return request.decode('utf-8')

	async def send(self, response: Any) -> None:
		await self._event_loop.sock_sendall(self._sock, str(response).encode('utf-8'))
