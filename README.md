# Local Mock

## About

A simple and lightweight mock server that allows you to create mock responses for your HTTP requests. It's easy to use and configure, and it's perfect for local development and testing.

## Features

-   **Easy to use:** Create a mock by simply adding a JSON file to the `mocks` directory.
-   **Automatic reload:** The server automatically reloads when you make changes to your mock files.
-   **Flexible configuration:** Configure the server's port and mock directory.
-   **Supports multiple HTTP methods:** GET, POST, PUT, DELETE.
-   **Query parameter matching:** Match requests based on query parameters.
-   **Response delay:** Simulate network latency by adding a delay to your responses.

## Getting Started

### Prerequisites

-   Python 3.7+

### Installation

1.  Clone the repository:
    ```bash
    git clone https://github.com/vitoralbano/local-mock.git
    ```
2.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

### Running the server

To start the server, run the following command:

```bash
python3 -m src
```

The server will start on `http://0.0.0.0:8000` by default.

## Configuration

The server can be configured using the `config.json` file. The following options are available:

-   `port`: The port to run the server on.
-   `mock_dir`: The directory where your mock files are located.

## Usage

To create a mock, add a JSON file to the `mocks` directory. The JSON file should have the following structure:

```json
{
  "request": {
    "method": "GET",
    "path": "/test",
    "queryParams": {
      "param1": "value1"
    }
  },
  "response": {
    "statusCode": 200,
    "delaySeconds": 0,
    "headers": {
      "Content-Type": "application/json"
    },
    "body": {
      "message": "Hello from mock"
    }
  }
}
```

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
