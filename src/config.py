
import json
import os

# Default configuration values
DEFAULT_CONFIG = {
    'host': 'localhost',
    'port': 8000,
    'mock_dir': 'mocks'
}

def load_config(config_path='config.json'):
    """Loads configuration from a given path, with fallbacks to defaults."""
    config = DEFAULT_CONFIG.copy()
    
    if os.path.exists(config_path):
        with open(config_path, 'r') as f:
            try:
                loaded_config = json.load(f)
                config.update(loaded_config)
            except json.JSONDecodeError:
                print(f"Warning: Could not decode {config_path}. Using default configuration.")
    else:
        print(f"Warning: {config_path} not found. Using default configuration.")


    return config

def reload_config(config_path='config.json'):
    """Reloads the configuration from a specific file and updates global vars."""
    global config, HOST, PORT, MOCK_DIR
    config = load_config(config_path)
    HOST = config.get('host')
    PORT = config.get('port')
    MOCK_DIR = config.get('mock_dir')


# Load the default configuration once when the module is imported
reload_config()
