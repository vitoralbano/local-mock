
import http.server
import json
import os
import time
from http import HTTPStatus
from urllib.parse import urlparse, parse_qs

from . import messages
from . import config

class MockRequestHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def _find_matching_mock(self):
        req_url = urlparse(self.path)
        req_path = req_url.path
        req_params = parse_qs(req_url.query)
        req_method = self.command

        for filename in os.listdir(config.MOCK_DIR):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(config.MOCK_DIR, filename)
            with open(filepath, 'r') as f:
                try:
                    mock_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"Warning: Could not decode {filepath}. Skipping.")
                    continue
            
            if not mock_data.get('enabled', True):
                continue
                
            mock_request = mock_data.get('request', {})
            if mock_request.get('method') == req_method and mock_request.get('path') == req_path:
                
                # Check query params
                mock_params = mock_request.get('queryParams', {})
                params_match = True
                for key, value in mock_params.items():
                    if key not in req_params or value not in req_params[key]:
                        params_match = False
                        break
                
                if params_match:
                    return mock_data

        return None

    def handle_request(self):
        start_time = time.time()
        
        mock_data = self._find_matching_mock()

        if not mock_data:
            status = HTTPStatus.NOT_FOUND
            self.send_error(status, messages.MOCK_NOT_FOUND)
            self._print_request_log(status, time.time() - start_time)
            return

        # --- Mock found, build response ---
        response_data = mock_data.get('response', {})
        status_code = response_data.get('statusCode', 200)
        delay = response_data.get('delaySeconds', 0)
        headers = response_data.get('headers', {})
        body = response_data.get('body', {})
        
        # Handle delay
        if delay > 0:
            time.sleep(delay)

        self.send_response(status_code)
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        
        if body:
            self.wfile.write(json.dumps(body).encode('utf-8'))

        self._print_request_log(status_code, time.time() - start_time)

    def _print_request_log(self, status, delay):
        """Prints a custom log message for the request."""
        print(messages.REQUEST_LOG.format(method=self.command, path=self.path, status=status, delay=delay))

    def log_request(self, code='-', size='-'):
        """Overrides the base class method to prevent automatic logging."""
        pass

def run(server_class=http.server.HTTPServer, handler_class=MockRequestHandler):
    server_address = (config.HOST, config.PORT)
    httpd = server_class(server_address, handler_class)
    
    print(messages.SERVER_START.format(port=config.PORT))
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print(messages.SERVER_STOP)
        httpd.server_close()

if __name__ == '__main__':
    run()
