import os
import time
import threading
from typing import Callable


class Monitor:
    def __init__(self, path: str, callback: Callable):
        self._path = path
        self._callback = callback
        self._file_states = {}
        self._thread = threading.Thread(target=self._watch, daemon=True)

    def start(self):
        """Starts the monitoring thread."""
        self._thread.start()

    def _watch(self):
        """Periodically scans the directory for changes."""
        # Initial scan to populate file states
        self._file_states = {
            f: os.path.getmtime(f) for f in self._get_current_files()
        }
        
        while True:
            self._check_for_changes()
            time.sleep(1)

    def _get_current_files(self):
        """Returns a set of current json file paths in the directory."""
        return {
            os.path.join(self._path, f)
            for f in os.listdir(self._path)
            if f.endswith(".json")
        }

    def _check_for_changes(self):
        """
        Checks for file modifications, creations, or deletions.
        """
        current_files = self._get_current_files()
        previous_files = set(self._file_states.keys())

        if current_files != previous_files:
            self._callback()
            return

        for file_path in current_files:
            try:
                last_modified = os.path.getmtime(file_path)
                if self._file_states.get(file_path) != last_modified:
                    self._callback()
                    return
            except FileNotFoundError:
                # If file is deleted between list and stat, it's a change.
                self._callback()
                return

