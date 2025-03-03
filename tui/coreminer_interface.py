import subprocess
import json
import threading
from queue import Queue

class CoreMinerProcess:
    def __init__(self, rust_binary_path: str):
        """Initialize the Rust process given a binary path."""
        self.process = subprocess.Popen(
            [rust_binary_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True
        )
        self.queue = Queue()
        threading.Thread(target=self._read_output, daemon=True).start()

    def _read_output(self):
        """Reads output from the Rust process and stores it in a queue."""
        while True:
            if self.process.stdout:
                line = self.process.stdout.readline().strip()
                if line:
                    self.queue.put(json.loads(line))

    def send_command(self, command: str):
        """Sends a JSON command to the Rust process."""
        if self.process.stdin:
            json_data = json.dumps({"command": command}) + "\n"
            self.process.stdin.write(json_data)
            self.process.stdin.flush()

    def get_response(self):
        """Retrieves a response from the queue."""
        if not self.queue.empty():
            return self.queue.get()
        return None