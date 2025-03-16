import subprocess
import json
import threading
from queue import Queue

# Import parser logic
from command_parser import CommandParser
from feedback_parser import FeedbackParser

class CoreMinerProcess:
    def __init__(self, data_store):
        """Initialize the Rust process given a binary path."""
        self.process = subprocess.Popen(
            ["cmserve"], 
            stdin=subprocess.PIPE, 
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, 
            text=True
        )

        self.data_store = data_store

        self.command_parser = CommandParser()
        self.feedback_parser = FeedbackParser(self.data_store)

        self.queue_feedback = Queue()
        self.queue_output = Queue()
        self.queue_stderr = Queue()
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()
    def _read_stdout(self):
        """Reads output from CoreMiner and stores it in a queue."""
        while True:
            if self.process.stdout:
                line_stdout = self.process.stdout.readline().strip()
                if line_stdout:
                    try:
                        # Try to parse as JSON
                        self.queue_feedback.put(json.loads(line_stdout))
                    except Exception as e:
                        print(e)

    def _read_stderr(self):
        """Reads output from CoreMiner and stores it in a queue."""
        while True:
            if self.process.stderr:
                line_stderr = self.process.stderr.readline().strip()
                if line_stderr:
                    try:
                        # Try to parse as JSON
                        self.queue_stderr.put(json.loads(line_stderr))
                    except json.JSONDecodeError:
                        # If not JSON, store as a regular string
                        self.queue_stderr.put(line_stderr)
                    except Exception as e:
                        print(e)

    def parse_command(self, command: str):
        """Parses the command, sends JSON to the Rust process if valid."""
        result_dict = self.command_parser.parse(command)
        if result_dict:
            # If the parser returned a dict, let's see if it has an error
            if "feedback" in result_dict:
                self.queue_feedback.put(result_dict)
            else:
                # Otherwise send to Rust
                self.send_command(json.dumps(result_dict))

    def send_command(self, json_command):
        """Sends a JSON command to the CoreMiner."""
        if self.process.stdin:
            self.process.stdin.write(json_command + "\n")
            self.process.stdin.flush()

    def get_response(self):
        """
        Retrieves a response from the queue. Whenever there's something in queue_feedback,
        we parse it using the FeedbackParser, which in turn updates the data store.
        """
        if not self.queue_feedback.empty():
            feedback = self.queue_feedback.get()
            self.feedback_parser.parse_feedback(feedback)
            return True
        return False