from aiosocknet import JSONResponse, HTTPStatus, pprintr


mascot = JSONResponse(HTTPStatus.OK, {
	'id': 30,
	'name': 'Tux',
	'company': {
		'name': 'Linux',
		'website': 'https://www.linux.org/',
	},
})
pprintr(mascot)


http_404 = JSONResponse(HTTPStatus.NOT_FOUND, {
	'description': HTTPStatus.NOT_FOUND.description,
})
pprintr(http_404)


todo = JSONResponse(HTTPStatus.OK,
	{'message': 'install archlinux'},
	headers={'CustomHeader': 'I use Arch btw'},
)
pprintr(todo)
