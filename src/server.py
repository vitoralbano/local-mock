
import http.server
import json
import os
import threading
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
        print(messages.REQUEST_LOG.format(method=self.command, path=self.path, status=status, delay=f"{delay:.4f}s"))

    def log_request(self, code='-', size='-'):
        """Overrides the base class method to prevent automatic logging."""
        pass

def run(stop_event, server_class=http.server.HTTPServer, handler_class=MockRequestHandler):
    """
    Sets up and runs the mock server until the stop_event is set.
    """
    server_address = ('', config.PORT)
    httpd = server_class(server_address, handler_class)

    # Run server in a separate thread so we can shut it down gracefully
    server_thread = threading.Thread(target=httpd.serve_forever)
    server_thread.daemon = True
    server_thread.start()

    print(messages.SERVER_START.format(port=config.PORT))

    try:
        # Wait for the stop event or a keyboard interrupt
        stop_event.wait()
    except KeyboardInterrupt:
        print(messages.SERVER_STOP)
    finally:
        # Gracefully shut down the server
        httpd.shutdown()
        httpd.server_close()
        server_thread.join()
