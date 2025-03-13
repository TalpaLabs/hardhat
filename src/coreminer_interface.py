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

        # Dispatch table: command -> function returning a dict
        command_table = {
            # Single-word commands
            "procmap":       lambda args: {"status": "ProcMap"},
            "pm":            lambda args: {"status": "ProcMap"},

            "backtrace":     lambda args: {"status": "Backtrace"},
            "bt":            lambda args: {"status": "Backtrace"},

            "continue":      lambda args: {"status": "Continue"},
            "cont":          lambda args: {"status": "Continue"},
            "c":             lambda args: {"status": "Continue"},

            "stepover":      lambda args: {"status": "StepOver"},
            "sov":           lambda args: {"status": "StepOver"},

            "stepout":       lambda args: {"status": "StepOut"},
            "so":            lambda args: {"status": "StepOut"},

            "stepinto":      lambda args: {"status": "StepInto"},
            "si":            lambda args: {"status": "StepInto"},

            "stepsingle":    lambda args: {"status": "StepSingle"},
            "step":          lambda args: {"status": "StepSingle"},
            "s":             lambda args: {"status": "StepSingle"},

            "getstack":      lambda args: {"status": "GetStack"},
            "stack":         lambda args: {"status": "GetStack"},

            "debuggerquit":  lambda args: {"status": "DebuggerQuit"},
            "quit":          lambda args: {"status": "DebuggerQuit"},
            "exit":          lambda args: {"status": "DebuggerQuit"},
            "q":             lambda args: {"status": "DebuggerQuit"},

            "info":          lambda args: {"status": "Infos"},

            # Complex commands
            "run":           self.parse_run,
            # "setbreakpoint": parse_setbreakpoint, ...
        }

        if cmd not in command_table:
            # Unknown command: queue an error and exit
            self.queue_feedback.put(json.dumps({
                "feedback": {
                    "Error": {
                        "error_type": "command",
                        "message": f"Unknown command: {cmd} {args}"
                    }
                }
            }))
            return

        # Call the parser function to build a dict
        parse_func = command_table[cmd]
        result_dict = parse_func(args)  # <--- CALL the function

        # If the parser function returned None or an empty dict, do nothing
        if not result_dict:
            return

        # If it returned an error with "feedback"
        if "feedback" in result_dict:
            self.queue_feedback.put(json.dumps(result_dict))
            return

        # Otherwise, it's a valid command
        self.send_command(json.dumps(result_dict))
        return 

    
    def parse_run(self, args: list[str]) -> dict:
        """
        "Run /bin/ls -la" -> 
        {"status": {"Run": ["/bin/ls", [ [47,101,116,99], [45,108,97] ] ]}}
        """
        if not args:
            self.queue_feedback.put(json.dumps({
                "feedback": {"Error":{"error_type": "command", "message": "Missing Arguments run PATH [ARGS]"}}
            }))
            return

        path = args[0]
        rest   = args[1:] 

        return {"status": {"Run": [path, rest]}}

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