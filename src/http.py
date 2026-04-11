from __future__ import annotations
# from http import HTTPStatus
import json
from typing import Any

from aiosocknet.src.models import JSONValue


CRLF = '\r\n'


class Request:
	...


def get_response(body: dict) -> str:
	CRLF = '\r\n'
	body_json = json.dumps(body, ensure_ascii=True)
	body_len = len(body_json)
	response = f'HTTP/1.1 200 OK{CRLF}Content-Length: {body_len}{CRLF}Connection: close{CRLF*2}{body_json}'
	return response


class Response:
	def __init__(
		self,
		body: JSONValue,
		headers: dict[str, Any] | None = None,
	) -> None:

		self._body = body
		self._json_str_body = self._json_to_string(body)
		self._body_len = len(self._json_str_body)

		_default_headers = {
			'Content-Length': self._body_len,
			'Connection': 'close',
		}

		if headers is None:
			headers = dict()

		self._headers = _default_headers | headers
		self._http_version = 'HTTP/1.1'

	def __repr__(self) -> str:
		cls_name = self.__class__.__name__
		return f'{cls_name}({self._body})'

	@property
	def body(self) -> JSONValue:
		return self._body

	@property
	def headers(self) -> JSONValue:
		return self.headers

	def _json_to_string(self, obj: JSONValue) -> str:
		return json.dumps(obj)
