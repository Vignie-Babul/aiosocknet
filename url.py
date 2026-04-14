import urllib.request

with urllib.request.urlopen('http://127.0.0.1:65535/tux') as response:
	print(response.read())
