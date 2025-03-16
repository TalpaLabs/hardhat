import json

class FeedbackParser:
    def __init__(self, data_store):
        self.data_store = data_store

    def parse_feedback(self, feedback_dict):
        """
        Parse the raw feedback (JSON dict or string) and update
        the store accordingly.
        """

        self.data_store.set_responses_coreminer(str(feedback_dict))

        feedback_data = feedback_dict["feedback"]
        if feedback_data == "Ok":
            return True

        for keyword, payload in feedback_data.items():
            if keyword == "Error":
                return self._parse_error(payload)
            elif keyword == "Registers":
                return self._parse_registers(payload)
            elif keyword == "Stack":
                return self._parse_stack(payload)
            else:
                # Default fallback if the keyword is unknown
                self.data_store.set_responses_coreminer(f"Unknown feedback key '{keyword}' -> {payload}")
                return False
            
    def _parse_error(self, register_dict):
        return False

    def _parse_registers(self, registers_dict):
        """
        Turn something like:
           {"cs": 51, "ds": 0, "eflags": 512, ...}
        into a readable multiline string.
        """
        lines = []
        for reg_name, reg_value in registers_dict.items():
            lines.append(f"  {reg_name}: {reg_value:0x}")

        self.data_store.set_registers("\n".join(lines))
        return True
    
    def _parse_stack(self, stack_dict):
        """
        Turn something like:
           {"cs": 51, "ds": 0, "eflags": 512, ...}
        into a readable multiline string.
        """
        start_addr = stack_dict["start_addr"]
        words = stack_dict["words"]
        lines = []
        for word in words:
            lines.append(f"  {start_addr:016x}: {word:016x}")
            start_addr += 8
        self.data_store.set_stack("\n".join(lines))
        return True
