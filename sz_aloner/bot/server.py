from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import urllib.parse as urlparse
#url = 'http://foo.appspot.com/abc?def=ghi'
#parsed = urlparse.urlparse(url)
#print(urlparse.parse_qs(parsed.query)['def'])

class testHTTPServer_RequestHandler(BaseHTTPRequestHandler):
 
	def do_GET(self):
		filename = self.path[1:9]
		if filename == 'telegram':
			parsed = urlparse.parse_qs(urlparse.urlparse(self.path).query)
			if 'username' in parsed:
				if 'act' in parsed:
					os.system("python bot/bot.py " + parsed['username'][0] + " " + parsed['act'][0])
		self.send_response(200)
		self.send_header('Content-type','text/html')
		self.end_headers()
		message = "Hello world!"
		self.wfile.write(bytes(message, "utf8"))
		return
 
def run():
	print('Starting server')

	server_address = ('127.0.0.1', 8080)
	httpd = HTTPServer(server_address, testHTTPServer_RequestHandler)
	print('Running server')
	httpd.serve_forever()

run()