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
            self.data_store.set_debuggee_output("CoreMiner: Ok")
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
            elif keyword == "ProcessMap":
                return self._parse_processmap(payload)
            elif keyword == "Backtrace":
                return self._parse_backtrace(payload)
            elif keyword == "Word":
                return self._parse_read_memory(payload)
            elif keyword == "Symbols":
                return self._parse_symbols(payload)
            elif keyword == "Variable":
                return self._parse_variable(payload)
            else:
                # Default fallback if the keyword is unknown
                self.data_store.set_responses_coreminer(f"Unknown feedback key '{keyword}' -> {payload}")
                return False
            
    def _parse_error(self, error_dict):
        self.data_store.set_debuggee_output(f"CoreMiner [Error]: {error_dict}")
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
    
    def _parse_processmap(self, procmap_dict):
        # Get summary values from the dictionary
        total_mapped = procmap_dict.get("total_mapped", 0)
        executable_regions = procmap_dict.get("executable_regions", 0)
        private_regions = procmap_dict.get("private_regions", 0)
        writable_regions = procmap_dict.get("writable_regions", 0)

        # Build header information
        output_lines = [
            "Process Memory Map:",
            f"  Total mapped memory: {total_mapped} bytes",
            f"  Executable regions: {executable_regions}",
            f"  Writable regions: {writable_regions}",
            f"  Private regions: {private_regions}",
            "",
            "Regions:"
        ]

        # Iterate over each region in the list
        regions = procmap_dict.get("regions", [])
        for idx, region in enumerate(regions, start=1):
            start_addr = region.get("start_address", 0)
            end_addr = region.get("end_address", 0)
            size = region.get("size", 0)
            offset = region.get("offset", 0)
            device = region.get("device", "N/A")
            inode = region.get("inode", "N/A")
            path = region.get("path")
            if path is None:
                path = "Anonymous"

            # Create a permissions string similar to the Linux maps file:
            # read (r), write (w), execute (x) and private/shared (p/s)
            perms = region.get("permissions", {})
            r = "r" if perms.get("read", False) else "-"
            w = "w" if perms.get("write", False) else "-"
            x = "x" if perms.get("execute", False) else "-"
            # Prefer private (p) over shared (s); otherwise use '-'
            if perms.get("private", False):
                ps = "p"
            elif perms.get("shared", False):
                ps = "s"
            else:
                ps = "-"
            perm_str = r + w + x + ps

            # Append the formatted region info
            output_lines.append(
                f"  {idx}. {path}\n"
                f"      Address Range: 0x{start_addr:016x} - 0x{end_addr:016x}\n"
                f"      Size: {size} bytes, Offset: {offset}, Device: {device}, Inode: {inode}\n"
                f"      Permissions: {perm_str}"
            )

        # Combine all lines into one output string
        output = "\n".join(output_lines)
        self.data_store.set_debuggee_output("CoreMiner:\n" +"ProcessMap: \n" + output)
        return True
    
    def _parse_backtrace(self, backtrace_dict):
        frames = backtrace_dict.get("frames", [])
        output_lines = ["Backtrace:"]
        
        for idx, frame in enumerate(frames, start=1):
            addr = frame.get("addr", 0)
            name = frame.get("name") or "<unknown>"
            start_addr = frame.get("start_addr")
            
            # Format the address as hex
            addr_str = f"0x{addr:016x}"
            # Format the start address if available, otherwise use "N/A"
            start_str = f"0x{start_addr:016x}" if start_addr is not None else "N/A"
            
            # Build a line for this frame
            output_lines.append(f"  {idx}. Address: {addr_str} | Function: {name} | Start: {start_str}")
        
        output = "\n".join(output_lines)
        self.data_store.set_debuggee_output("CoreMiner:\n" + output)
        return True
    
    def _parse_read_memory(self, word_value):
        try:
            # Convert the integer to a hex string formatted with 16 digits, with a 0x prefix.
            hex_word = f"0x{int(word_value):016x}"
        except (ValueError, TypeError):
            hex_word = "Invalid word value"
        
        # Set the output in the data store.
        self.data_store.set_debuggee_output("CoreMiner:\n" + f"Memory word: {hex_word}")
        return True
    
    def _parse_symbols(self, symbols):
        """
        Parse the symbols feedback and build a human-readable tree of symbols.
        
        The expected payload is a list of symbol entries where each symbol is a dict
        with keys like 'kind', 'name', 'offset', 'datatype', 'low_addr', 'high_addr', and
        'children' (which is a list of child symbols).
        """

        # Build the output from the list of top-level symbols
        output_lines = ["Symbols:"]
        for symbol in symbols:
            output_lines.extend(self.format_symbols(symbol))
            
        output = "\n".join(output_lines)
        self.data_store.set_debuggee_output("CoreMiner:\n" + output)
        return True
    
    def format_symbols(self, symbol, indent=0):
        indent_str = "  " * indent
        # Use name if available, otherwise display as <anonymous>
        name = symbol.get("name") if symbol.get("name") is not None else "<anonymous>"
        kind = symbol.get("kind", "<unknown>")
        offset = symbol.get("offset")
        datatype = symbol.get("datatype")
        low_addr = symbol.get("low_addr")
        high_addr = symbol.get("high_addr")

        # Build the base description for the symbol
        line = f"{indent_str}{kind}: {name}"
        if offset is not None:
            line += f", offset: {offset}"
        if datatype is not None:
            line += f", datatype: {datatype}"
        if low_addr is not None or high_addr is not None:
            low_str = f"0x{low_addr:016x}" if low_addr is not None else "?"
            high_str = f"0x{high_addr:016x}" if high_addr is not None else "?"
            line += f", range: {low_str} - {high_str}"

        # Start with this symbol's line
        lines = [line]
        # Recursively process any children symbols
        for child in symbol.get("children", []):
            lines.extend(self.format_symbols(child, indent=indent + 1))
        return lines

    def _parse_variable(self, variable_dict):
        """
        Parse the variable feedback and format its bytes.
        
        The expected payload is a dictionary with a 'Bytes' key that contains a list
        of integer values representing the variable's content.
        """
        # Retrieve the list of bytes from the dictionary
        bytes_list = variable_dict.get("Bytes", [])
        
        # Convert each byte to a two-digit hexadecimal string and join them with a space.
        hex_bytes = " ".join(f"{b:02x}" for b in bytes_list)
        
        # Build the output string
        output = f"Variable: {hex_bytes}"
        
        # Send the output to the data store
        self.data_store.set_debuggee_output("CoreMiner:\n" + output)
        return True