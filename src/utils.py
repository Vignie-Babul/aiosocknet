from aiosocknet.src.http import JSONResponse
from pprint import pp


def pprintr(obj: JSONResponse) -> None:
	print(obj.headers, end='\n\n')
	pp(obj.body, sort_dicts=False)
	print('\n')
