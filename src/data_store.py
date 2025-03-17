from typing import Optional

class DataStore:
    """
    A container for all shared state/data.
    Widgets can query this to get the information they need.
    """

    def __init__(self):
        self.responses_coreminer: Optional[str] = None
        self.registers = ""
        self.stack = ""
        self.rip = ""
        self.debuggee_output = ""
        self.disassembly= ""

    def set_responses_coreminer(self, response: str) -> None:
        """Appends the new response to responses"""
        if self.responses_coreminer:
            self.responses_coreminer += f"\n{response}"
        else:
            self.responses_coreminer = response

    def get_responses_coreminer(self) -> str:
        """Retrieve the responses."""
        return self.responses_coreminer
    
    def set_registers(self, response: str) -> None:
        self.registers = response

    def get_registers(self) -> str:
        """Retrieve the Registers."""
        return self.registers
    
    def set_stack(self, response: str) -> None:
        self.stack = response

    def get_stack(self) -> str:
        return self.stack
    
    def set_debuggee_output(self, response: str) -> None:
        if self.debuggee_output:
            self.debuggee_output += f"\n{response}"
        else:
            self.debuggee_output = response

    def get_debuggee_output(self) -> str:
        return self.debuggee_output
    
    def set_disassembly(self, response: str) -> None:
        self.disassembly = response
    
    def get_disassembly(self) -> str:
        return self.disassembly
    
    def set_rip(self, response: str) -> None:
        self.rip = response

    def get_rip(self) -> str:
        return self.rip
