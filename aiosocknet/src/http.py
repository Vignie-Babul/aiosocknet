from __future__ import annotations
from http import HTTPStatus
import json
from typing import Any

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
