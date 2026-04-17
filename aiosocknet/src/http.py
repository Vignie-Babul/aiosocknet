from __future__ import annotations
from collections.abc import Callable
import logging
from http import HTTPStatus
import json
from typing import Any
import re

from aiosocknet.src.models import JSONValue


CRLF = '\r\n'


class JSONResponse:
	def __init__(
		self,
		http_code: HTTPStatus,
		body: JSONValue,
		headers: dict[str, Any] | None = None,
	) -> None:

		self._body = body
		self._json_str_body = self._json_to_string(body)
		self._body_len = len(self._json_str_body)

		_default_headers = {
			'Content-Type': 'application/json; charset=utf-8',
			'Content-Length': self._body_len,
			'Connection': 'close',
		}

		if headers is None:
			headers = dict()

		_http_version = 'HTTP/1.1'
		_head = f'{_http_version} {http_code.value} {http_code.phrase}'
		_headers = self._headers_to_str(_default_headers | headers)
		self._headers = f'{_head}{CRLF}{_headers}'

		self._response = f'{self._headers}{CRLF*2}{self._json_str_body}'

	def __repr__(self) -> str:
		cls_name = self.__class__.__name__
		return f'{cls_name}({self._response})'

	def __str__(self) -> str:
		return self._response

	@property
	def headers(self):
		return self._headers

	@property
	def body(self):
		return self._body

	def _json_to_string(self, obj: JSONValue) -> str:
		return json.dumps(obj, ensure_ascii=False)

	def _headers_to_str(self, headers: dict[str, Any]) -> str:
		return f'{CRLF}'.join((f'{k}: {v}' for k, v in headers.items()))


class APIRouter:
	def __init__(self) -> None:
		self._log = logging.getLogger(__name__)

		self._routes = {}
		self._compiled = []

	def _get_path(self, request: str) -> str:
		return request.split('HTTP/1.1')[0].split()[1]

	def _compile_template(self, template: str):
		parts = []
		last = 0

		for m in re.finditer(r'\{([^}]+)\}', template):
			parts.append(re.escape(template[last:m.start()]))
			name = m.group(1)

			if not re.match(r'^[A-Za-z_]\w*$', name):
				raise ValueError(f'invalid parameter name: {name}')

			parts.append(f'(?P<{name}>[^/]+)')
			last = m.end()

		parts.append(re.escape(template[last:]))
		pattern = ''.join(parts)
		return re.compile(f'^{pattern}$')

	def _dispatch(self, path: str) -> Any:
		for pattern, func in self._compiled:
			matched = pattern.match(path)
			if matched:
				kwargs = matched.groupdict()
				return func(**kwargs)

		return JSONResponse(HTTPStatus.NOT_FOUND, {
			'status': HTTPStatus.NOT_FOUND.value,
			'description': HTTPStatus.NOT_FOUND.description,
		})

	def route(self, path: str) -> Callable:
		def wrapper(function) -> Callable: 
			self._routes[path] = function
			return function

		return wrapper

	def get(self, request: str) -> Any | None:
		self._compiled = [
			(
				self._compile_template(temp),
				func,
			) for temp, func in self._routes.items()
		]

		path = self._get_path(request)
		return self._dispatch(path)
