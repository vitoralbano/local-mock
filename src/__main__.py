import os
import sys
import threading
from .server import run
from .monitor import Monitor
from . import config
from . import messages

def restart():
    """Restarts the current program, with the same arguments."""
    print(messages.SERVER_RELOADING.format(reason="changes in mock files"))
    
    executable = sys.executable
    # sys.argv contains the script name and arguments.
    # The first argument to execv is the program to execute.
    # The second is a list of strings, which becomes the new sys.argv.
    os.execv(executable, [executable] + sys.argv)

if __name__ == '__main__':
    stop_event = threading.Event()

    def reload_callback():
        """Callback to trigger the server shutdown."""
        if not stop_event.is_set():
            stop_event.set()

    # The monitor needs to know the path to the mocks
    mock_path = config.MOCK_DIR
    
    monitor = Monitor(path=mock_path, callback=reload_callback)
    monitor.start()

    # The server runs, blocking until stop_event is set or Ctrl+C is pressed
    run(stop_event=stop_event)

    # If the stop_event was set, it means the monitor triggered a reload.
    if stop_event.is_set():
        restart()