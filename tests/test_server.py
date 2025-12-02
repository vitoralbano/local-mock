
import unittest
import json
import os
import threading
import time
from http import HTTPStatus

import requests

from src.server import run

class TestMockServer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8080
        cls.server_thread = threading.Thread(target=run, kwargs={'port': cls.port})
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1) # Wait for the server to start

    def test_successful_response(self):
        # Create a mock file
        mock_file_path = 'mocks/test_success.json'
        mock_data = {
            "status_code": 200,
            "response": {
                "headers": {"Content-Type": "application/json"},
                "body": {"message": "Success"}
            }
        }
        with open(mock_file_path, 'w') as f:
            json.dump(mock_data, f)

        response = requests.get(f'http://localhost:{self.port}/test_success')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), mock_data['response']['body'])

        os.remove(mock_file_path)

    def test_mock_not_found(self):
        response = requests.get(f'http://localhost:{self.port}/non_existent_mock')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_invalid_json(self):
        # Create a mock file with invalid JSON
        mock_file_path = 'mocks/test_invalid.json'
        with open(mock_file_path, 'w') as f:
            f.write('{"invalid": json}')

        response = requests.get(f'http://localhost:{self.port}/test_invalid')

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

        os.remove(mock_file_path)

if __name__ == '__main__':
    unittest.main()
