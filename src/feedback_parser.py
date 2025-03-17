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
            elif keyword == "Disassembly":
                return self._parse_disassembly(payload)
            else:
                # Default fallback if the keyword is unknown
                self.data_store.set_responses_coreminer(f"Unknown feedback key '{keyword}' -> {payload}")
                return False
            
    def _parse_error(self, register_dict):
        return False

    def _parse_registers(self, registers_dict):
        lines = []
        for reg_name, reg_value in registers_dict.items():
            lines.append(f"  {reg_name}: {reg_value:0x}")
            if reg_name == "rip":
                self.data_store.set_rip(reg_value)

        self.data_store.set_registers("\n".join(lines))
        return True
    
    def _parse_stack(self, stack_dict):
        start_addr = stack_dict["start_addr"]
        words = stack_dict["words"]
        lines = []
        for word in words:
            lines.append(f"  {start_addr:016x}: {word:016x}")
            start_addr += 8
        self.data_store.set_stack("\n".join(lines))
        return True

    def _parse_disassembly(self, disasm_dict):
        """
        Format each instruction into columns:
        - Address
        - Hex bytes
        - Mnemonic (optional column)
        - Operands
        - Breakpoint marker (if True)
        """

        ADDRESS_COL_WIDTH = 21
        BYTES_COL_WIDTH   = 22
        MNEMONIC_COL_WIDTH = 8

        lines = []
        for entry in disasm_dict["vec"]:
            address       = entry[0]     # e.g. 140180160845120
            bytes_list    = entry[1]     # e.g. [72, 137, 231]
            tokens        = entry[2]     # list of dicts with { kind: "...", text: "..." }
            has_breakpoint = entry[3]    # True or False

            # 1) Format address as hex, left-justify in a fixed width
            # Add (*) if there is a breakpoint in the line
            if has_breakpoint:
                address_str = f"{address:016x}(*)"
            else:
                address_str = f"{address:016x}"
            address_col = f"{address_str:<{ADDRESS_COL_WIDTH}}"

            # 2) Convert bytes to something like "48 89 e7"
            byte_str = " ".join(f"{b:02x}" for b in bytes_list)
            bytes_col = f"{byte_str:<{BYTES_COL_WIDTH}}"

            # 3) Separate the first 'Mnemonic' token (if present) from the rest
            mnemonic_text = ""
            operand_text = ""
            found_mnemonic = False
            for token in tokens:
                if token.get("kind") == "Mnemonic" and not found_mnemonic:
                    mnemonic_text = token["text"].strip()  # e.g. "mov"
                    found_mnemonic = True
                else:
                    
                    operand_text += token["text"]

            # 4) Create a column for the mnemonic, then follow it with the operand text
            mnemonic_col = f"{mnemonic_text:<{MNEMONIC_COL_WIDTH}}"
            # Trim extra spaces
            operand_text = operand_text.strip()

            # 5) Combine them into one line
            line_str = f"{address_col}{bytes_col}{mnemonic_col}{operand_text}"

            lines.append(line_str)

        # Join and store the result
        disassembly_str = "\n".join(lines)
        self.data_store.set_disassembly(disassembly_str)

        return True