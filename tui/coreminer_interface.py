import subprocess
import json
import threading
from queue import Queue

class CoreMinerProcess:
    def __init__(self):
        """Initialize the Rust process given a binary path."""
        self.process = subprocess.Popen(
            ["cmserve"], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, 
            text=True
        )
        self.queue = Queue()
        threading.Thread(target=self._read_output, daemon=True).start()

    def _read_output(self):
        """Reads output from CoreMiner and stores it in a queue."""
        while True:
            if self.process.stdout:
                line = self.process.stdout.readline().strip()
                if line:
                    try:
                        # Try to parse as JSON
                        self.queue.put(json.loads(line))
                    except json.JSONDecodeError:
                        # If not JSON, store as a regular string
                        self.queue.put(line)

    def send_command(self, command: str):
        """Sends a JSON command to the CoreMiner."""
        if self.process.stdin:
            json_data = json.dumps({"status": f"{command}"}) + "\n"
            self.process.stdin.write(json_data)
            self.process.stdin.flush()

    def get_response(self):
        """Retrieves a response from the queue."""
        if not self.queue.empty():
            return self.queue.get()
        return None