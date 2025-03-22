from typing import Optional

class DataStore:
    """
    A container for all shared state and data used across the application.

    This class stores information such as responses from CoreMiner, register values, the stack,
    the instruction pointer (RIP), output messages, and disassembly information. Widgets and other
    components can query and update this shared data store to reflect the current state of the debuggee.
    """

    def __init__(self):
        """
        Initialize the DataStore with default empty values.

        Attributes:
            responses_coreminer (Optional[str]): Stores concatenated responses from CoreMiner. Initialized as None.
            registers (str): Stores the current register values as a string.
            stack (str): Stores the current stack as a string.
            rip (str): Stores the current instruction pointer (RIP) as a string.
            output (str): Stores debuggee output messages.
            disassembly (str): Stores disassembly information.
        """
        self.responses_coreminer: Optional[str] = None
        self.registers = ""
        self.stack = ""
        self.rip = ""
        self.output = ""
        self.disassembly = ""
        self.backtrace = ""

    def set_responses_coreminer(self, response: str) -> None:
        """
        Append a new response from CoreMiner to the stored responses.

        If responses already exist, the new response is appended on a new line.
        Otherwise, the response is set as the initial value.

        Args:
            response (str): The response string from CoreMiner to be added.
        """
        if self.responses_coreminer:
            self.responses_coreminer += f"\n{response}"
        else:
            self.responses_coreminer = response

    def get_responses_coreminer(self) -> str:
        return self.responses_coreminer
    
    def set_registers(self, response: str) -> None:
        self.registers = response

    def get_registers(self) -> str:
        return self.registers
    
    def set_stack(self, response: str) -> None:
        self.stack = response

    def get_stack(self) -> str:
        return self.stack
    
    def set_output(self, response: str) -> None:
        """
        Append a new output message to the stored debuggee output.

        If output already exists, the new message is appended on a new line.
        Otherwise, the response is set as the initial output.

        Args:
            response (str): The output message to be added.
        """
        if self.output:
            self.output += f"\n{response}"
        else:
            self.output = response

    def get_output(self) -> str:
        return self.output
    
    def set_disassembly(self, response: str) -> None:
        self.disassembly = response
    
    def get_disassembly(self) -> str:
        return self.disassembly
    
    def set_rip(self, response: str) -> None:
        self.rip = response

    def get_rip(self) -> str:
        return self.rip
    
    def set_backtrace(self, response: str) -> None:
        self.backtrace = response

    def get_backtrace(self) -> str:
        return self.backtrace
