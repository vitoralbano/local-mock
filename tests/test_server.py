
import unittest
import json
import os
import shutil
import threading
import time
from http import HTTPStatus

import requests

from src import config
from src.server import run

class TestMockServer(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load test configuration
        config.reload_config('config_test.json')

        # Create test mock directory
        if not os.path.exists(config.MOCK_DIR):
            os.makedirs(config.MOCK_DIR)

        # Start server in a separate thread
        cls.server_thread = threading.Thread(target=run)
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1)  # Wait for the server to start

    @classmethod
    def tearDownClass(cls):
        # Clean up test mock directory
        if os.path.exists(config.MOCK_DIR):
            shutil.rmtree(config.MOCK_DIR)
        
        # Restore default configuration
        config.reload_config()

    def test_successful_response(self):
        # Create a mock file
        mock_file_path = os.path.join(config.MOCK_DIR, 'test_success.json')
        mock_data = {
            "status_code": 200,
            "response": {
                "headers": {"Content-Type": "application/json"},
                "body": {"message": "Success"}
            }
        }
        with open(mock_file_path, 'w') as f:
            json.dump(mock_data, f)

        response = requests.get(f'http://{config.HOST}:{config.PORT}/test_success')

        self.assertEqual(response.status_code, HTTPStatus.OK)
        self.assertEqual(response.json(), mock_data['response']['body'])

        os.remove(mock_file_path)

    def test_mock_not_found(self):
        response = requests.get(f'http://{config.HOST}:{config.PORT}/non_existent_mock')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_invalid_json(self):
        # Create a mock file with invalid JSON
        mock_file_path = os.path.join(config.MOCK_DIR, 'test_invalid.json')
        with open(mock_file_path, 'w') as f:
            f.write('{"invalid": json}')

        response = requests.get(f'http://{config.HOST}:{config.PORT}/test_invalid')

        self.assertEqual(response.status_code, HTTPStatus.INTERNAL_SERVER_ERROR)

        os.remove(mock_file_path)

if __name__ == '__main__':
    unittest.main()
