
import http.server
import json
import os
import time
from http import HTTPStatus

from . import messages

class MockRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def handle_request(self):
        start_time = time.time()
        
        mock_file_path = self.get_mock_file_path()

        if not os.path.exists(mock_file_path):
            self.send_error(HTTPStatus.NOT_FOUND, messages.MOCK_NOT_FOUND)
            self.log_request(HTTPStatus.NOT_FOUND, time.time() - start_time)
            return

        try:
            with open(mock_file_path, 'r') as f:
                mock_data = json.load(f)
        except json.JSONDecodeError as e:
            error_message = messages.JSON_DECODE_ERROR.format(path=mock_file_path, error=e)
            self.send_error(HTTPStatus.INTERNAL_SERVER_ERROR, error_message)
            self.log_request(HTTPStatus.INTERNAL_SERVER_ERROR, time.time() - start_time)
            return

        response_data = mock_data.get('response', {})
        status_code = mock_data.get('status_code', 200)
        headers = response_data.get('headers', {})
        body = response_data.get('body', {})

        self.send_response(status_code)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        
        if body:
            self.wfile.write(json.dumps(body).encode('utf-8'))

        self.log_request(status_code, time.time() - start_time)

    def get_mock_file_path(self):
        # Normalize path and remove leading slash
        path = self.path.lstrip('/')
        if not path:
            path = 'index'
        
        return os.path.join('mocks', f"{path}.json")

    def log_request(self, status, delay):
        print(messages.REQUEST_LOG.format(method=self.command, path=self.path, status=status, delay=delay))

def run(server_class=http.server.HTTPServer, handler_class=MockRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    
    print(messages.SERVER_START.format(port=port))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(messages.SERVER_STOP)
        httpd.server_close()

if __name__ == '__main__':
    run()
