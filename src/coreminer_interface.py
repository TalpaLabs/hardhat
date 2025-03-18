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
        self.command_finished = True

        self.command_parser = CommandParser()
        self.feedback_parser = FeedbackParser(self.data_store)

        self.queue_feedback = Queue()
        self.queue_output = Queue()
        self.queue_stderr = Queue()
        self.queue_commands = Queue()
        threading.Thread(target=self._read_stdout, daemon=True).start()
        threading.Thread(target=self._read_stderr, daemon=True).start()
        threading.Thread(target=self._send_command, daemon=True).start()
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
                        self.queue_output.put(str(line_stdout))

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
        result_dict, reload_basic_info = self.command_parser.parse(command)
        if result_dict:
            # If the parser returned a dict, let's see if it has an error --> returna feedback
            if "feedback" in result_dict:
                self.queue_feedback.put(result_dict)
            else:
                # Otherwise send to Rust
                self.queue_commands.put((json.dumps(result_dict)))
                if reload_basic_info == True:
                    self.reload_basic_info()

    def _send_command(self):
        """Sends a JSON command to the CoreMiner."""
        while True:
            if self.process.stdin:
                if not self.queue_commands.empty() and self.command_finished == True:
                    command = self.queue_commands.get()
                    self.process.stdin.write(command + "\n")
                    self.process.stdin.flush()
                    self.command_finished = False

    def get_response(self):
        """
        Retrieves a response from the queue. Whenever there's something in queue_feedback,
        we parse it using the FeedbackParser, which in turn updates the data store.
        """
        if not self.queue_feedback.empty():
            feedback = self.queue_feedback.get()
            executed_successfull = self.feedback_parser.parse_feedback(feedback)
            if executed_successfull:
                self.command_finished = True
                if self.queue_commands.empty():
                    return True
            else:  
                while not self.queue_commands.empty():
                    self.queue_commands.get() 
                self.command_finished = True
                return True
        
        # Check for Output
        if not self.queue_output.empty():
            output = self.queue_output.get()
            self.data_store.set_debuggee_output("Debuggee: " + output)
            if self.queue_output.empty():
                return True
        return False
    
    def reload_basic_info(self):
        self.queue_commands.put((json.dumps({"status": "DumpRegisters"})))
        self.queue_commands.put((json.dumps({"status": "GetStack"})))
        return