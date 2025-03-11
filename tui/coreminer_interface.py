import shlex
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
                    except json.JSONDecodeError:
                        # If not JSON, store as a regular string
                        self.queue_output.put(line_stdout)
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
        """
        Turn a user-typed command like:
        "SetBreakPoint 0xDEADBEEF"
        into JSON like:
        {"status": {"SetBreakPoint": 3735928559}}
        """
        tokens = shlex.split(command)
        if not tokens:
            return ""

        cmd = tokens[0].lower()
        args = tokens[1:]

        # Dispatch table: keys are command names,
        # values are functions that return a dict
        command_table = {
            "procmap":       lambda args: {"status": "ProcMap"},
            "backtrace":     lambda args: {"status": "Backtrace"},
            "continue":      lambda args: {"status": "Continue"},
            #"setbreakpoint": parse_setbreakpoint,
            #"run":           parse_run,
            # ...
        }

        if cmd not in command_table:
            # Unknown command
            self.send_command(json.dumps({"status": f"Unknown command: {tokens[0]}"}))
            return

        # Call the function to build a dict
        result_dict = command_table[cmd](args)
        self.send_command(json.dumps(result_dict))
        return 

    def send_command(self, json_command):
        """Sends a JSON command to the CoreMiner."""
        if self.process.stdin:
            self.process.stdin.write(json_command + "\n")
            self.process.stdin.flush()

    def get_response(self):
        """Retrieves a response from the queue."""
        if not self.queue_feedback.empty():
            return self.queue_feedback.get()
        return None