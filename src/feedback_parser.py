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
            return

        parsed_messages = []

        for keyword, payload in feedback_data.items():
            if keyword == "Registers":
                self._parse_registers(payload)
            elif keyword == "ProcMap":
                parsed_messages.append(self._parse_procmap(payload))
            else:
                # Default fallback if the keyword is unknown
                self.data_store.set_responses_coreminer(f"Unknown feedback key '{keyword}' -> {payload}")

    def _parse_registers(self, registers_dict):
        """
        Turn something like:
           {"cs": 51, "ds": 0, "eflags": 512, ...}
        into a readable multiline string.
        """
        lines = []
        for reg_name, reg_value in registers_dict.items():
            lines.append(f"  {reg_name}: {reg_value}")

        self.data_store.set_registers("\n".join(lines))
        return 