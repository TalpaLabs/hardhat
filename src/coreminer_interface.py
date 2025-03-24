"""
Module for managing the CoreMiner debugger process.

This module defines the CoreMinerProcess class, which is responsible for launching and communicating
with CoreMiner. It sets up subprocess I/O, spawns background threads to continuously read stdout and stderr, 
It also is responsible to send the JSON commands to the CoreMiners stdin. To pasre user commands and CoreMiner 
JSON feedback it uses the CommandParser and FeedbackParser class.  to handle communication and update the applications data store accordingly.
"""

import time
import subprocess
import json
import threading
from queue import Queue
import atexit

# Import parser logic
from command_parser import CommandParser
from feedback_parser import FeedbackParser


class CoreMinerProcess:
    """
    Manages the CoreMiner process and handles communication between the CoreMiner debugger and the HardHat TUI.

    This class launches the CoreMiner process, sets up I/O queues and background threads for reading
    stdout and stderr, and provides methods to parse and send commands to the process. It also retrieves
    and processes feedback from the process to update the data store.

    Attributes:
        process (subprocess.Popen): The subprocess running the CoreMiner binary.
        data_store: The shared data store used for updating debuggee output and other state information.
        command_finished (bool): Flag indicating whether the previous command has finished executing.
        command_parser (CommandParser): An instance used to parse text commands into JSON commands.
        feedback_parser (FeedbackParser): An instance used to process JSON feedback from the CoreMiner.
        queue_feedback (Queue): Queue for storing JSON feedback messages.
        queue_output (Queue): Queue for storing non-JSON stdout messages.
        queue_stderr (Queue): Queue for storing stderr messages.
        queue_commands (Queue): Queue for storing JSON commands to send to the process.
    """

    def __init__(self, data_store):
        """
        Initialize the CoreMinerProcess instance and launch the CoreMiner subprocess.

        The process is started with pipes for stdin, stdout, and stderr. The process is also registered
        for termination upon program exit. Command and feedback parsers are initialized, and background threads
        are started to handle asynchronous reading of the process's output and sending of commands.

        Args:
            data_store: An object used to store and update information received from the CoreMiner process.
        """
        self.process = subprocess.Popen(
            ["cmserve", "--logfile" , "/tmp/harthat_cm.log"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        atexit.register(lambda: self.process.terminate())

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
        """
        Continuously read lines from the CoreMiner process's stdout.

        Each line read is stripped of whitespace and then attempted to be parsed as JSON. If successful,
        line read is a feedback from the CoreMiner and is added to the feedback queue; otherwise, the line 
        is interpreted as output from the debuggee and added to the output queue.
        """
        while True:
            time.sleep(0.01)
            if self.process.stdout:
                line_stdout = self.process.stdout.readline().strip()
                if line_stdout:
                    try:
                        # Try to parse as JSON
                        self.queue_feedback.put(json.loads(line_stdout))
                    except Exception as e:
                        self.queue_output.put(str(line_stdout))

    def _read_stderr(self):
        """
        Continuously read lines from the CoreMiner process's stderr.

        Each line read is stripped of whitespace and then attempted to be parsed as JSON. If JSON parsing fails,
        the raw string is added to the stderr queue.
        """
        while True:
            time.sleep(0.01)
            if self.process.stderr:
                line_stderr = self.process.stderr.readline().strip()
                if line_stderr:
                    try:
                        # Try to parse as JSON
                        self.queue_stderr.put(json.loads(line_stderr))
                    except json.JSONDecodeError:
                        # If not JSON, store as a regular string
                        self.queue_stderr.put(line_stderr)

    def parse_command(self, command: str):
        """
        Parse a command string and send the corresponding JSON command to the CoreMiner process if valid.

        The command string is parsed using the CommandParser. If the parsed result indicates an error (i.e.,
        contains a "feedback" key), the error feedback is added to the feedback queue. Otherwise, the
        resulting JSON command is queued for sendingto the CoreMiner. If the command requires reloading 
        basic information, the reload_basic_info method is invoked.

        Args:
            command (str): The input command string provided by the user.
        """
        self.data_store.set_output(f"--> {command}")
        result_dict, reload_basic_info = self.command_parser.parse(command)
        if result_dict:
            # If the parser returned a dict, check for an error and return feedback if present.
            if "feedback" in result_dict:
                self.queue_feedback.put(result_dict)
            else:
                # Otherwise, send the valid JSON command to the Rust process.
                self.queue_commands.put((json.dumps(result_dict)))
                if reload_basic_info == True:
                    self.reload_basic_info()

    def _send_command(self):
        """
        Continuously send JSON commands from the command queue to the CoreMiner process.

        This method checks if there are any commands queued and if the previous command has finished executing.
        When both conditions are met, the next command is written to the process's stdin and flushed.
        """
        while True:
            time.sleep(0.01)
            if self.process.stdin:
                if not self.queue_commands.empty() and self.command_finished == True:
                    command = self.queue_commands.get()
                    self.process.stdin.write(command + "\n")
                    self.process.stdin.flush()
                    self.command_finished = False
                    self.data_store.set_responses_coreminer(command)

    def get_response(self):
        """
        Retrieve and process responses from the CoreMiner process.

        This method checks for JSON feedback in the feedback queue and processes it using the FeedbackParser,
        which updates the data store. If a command executes successfully, the command_finished flag is set.
        Additionally, if there is non-JSON output in the output queue, it updates the debuggee output in the data store.
        The method returns True when a complete response has been processed and the command queue is empty to trigger
        the TUI to reload the information of each widget. Due to performance issues we only update the widgets when
        the comamnd queue is empty insetad of after every command.

        Returns:
            bool: True if a response (feedback or output) was processed and the command is finished, False otherwise.
        """
        # Check for non-JSON output from the debuggee
        while not self.queue_output.empty():
            output = self.queue_output.get()
            self.data_store.set_output("[d]: " + output)
            if self.queue_output.empty():
                return True
            
        while not self.queue_stderr.empty():
            output = self.queue_stderr.get()
            self.data_store.set_output("[d][!]: " + output)
            if self.queue_stderr.empty():
                return True

        if not self.queue_feedback.empty():
            feedback = self.queue_feedback.get()
            executed_successfull = self.feedback_parser.parse_feedback(
                feedback)
            if executed_successfull:
                self.command_finished = True
                if self.queue_commands.empty():  # Only update TUI when the commands queue is empty
                    return True
            else:  # command unsuccessfull clear commands queue and send signal TRUE to update content of the widgets
                while not self.queue_commands.empty():
                    self.queue_commands.get()
                self.command_finished = True
                return True
        return False

    def reload_basic_info(self):
        """
        Enqueue commands to reload basic information from the debuggee.
        This method queues commands to retrieve the current register values and the stack from the debuggee.
        """
        self.queue_commands.put((json.dumps({"status": "DumpRegisters"})))
        self.queue_commands.put((json.dumps({"status": "GetStack"})))
        self.queue_commands.put((json.dumps({"status": "Backtrace"})))
        return
