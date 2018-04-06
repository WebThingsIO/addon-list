#!/usr/bin/env python3

from http.server import HTTPServer, SimpleHTTPRequestHandler


class CORSRequestHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)


if __name__ == '__main__':
    addr = ('127.0.0.1', 8088)
    httpd = HTTPServer(addr, CORSRequestHandler)

    print('Change your gateway config as such:\n'
          '\n'
          '  addonManager: {\n'
          '    ...\n'
          '    listUrl: \'http://127.0.0.1:8088/list.json\',\n'
          '    ...\n'
          '  },\n')
    httpd.serve_forever()
