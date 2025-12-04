# src/messages.py

# Server messages
SERVER_START = "Starting mock server on http://0.0.0.0:{port}..."
SERVER_STOP = "\nStopping server..."
SERVER_RELOADING = "Reloading server due to {reason}..."

# Request log format
REQUEST_LOG = "{method} {path} - {status} in {delay:.4f}s"

# Error messages
MOCK_NOT_FOUND = "Mock file not found"
JSON_DECODE_ERROR = "Error decoding JSON from {path}: {error}"
