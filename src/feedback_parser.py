class FeedbackParser:
    """
    Parses and processes feedback received from the CoreMiner process.

    This class receives feedback as a JSON dictionary (or string), parses it to determine the type of feedback,
    and updates the shared data store accordingly. Feedback types include errors, register values, stack information,
    disassembly output, process memory maps, backtraces, memory reads, symbols, variables, and plugin lists.
    """

    def __init__(self, data_store):
        """
        Initialize the FeedbackParser with a reference to the shared data store.

        Args:
            data_store: An object that holds shared state and data; it is updated based on the parsed feedback.
        """
        self.data_store = data_store

    def parse_feedback(self, feedback_dict):
        """
        Parse the raw feedback and update the data store accordingly.

        The feedback is expected to be a JSON dictionary. The method first stores the raw feedback in the data store.
        It then checks if the feedback is a simple "Ok" response or contains specific keys, and calls the appropriate
        parsing method based on the feedback keyword.

        Args:
            feedback_dict (dict): The feedback received from CoreMiner.

        Returns:
            bool: True if the feedback indicates successful execution; False otherwise.
        """
        self.data_store.set_responses_coreminer(str(feedback_dict))
        feedback_data = feedback_dict["feedback"]
        if feedback_data == "Ok":
            self.data_store.set_output("CoreMiner: Ok")
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
            elif keyword == "PluginList":
                return self._parse_plugin_list(payload)
            else:
                # Default fallback if the keyword is unknown
                self.data_store.set_responses_coreminer(f"Unknown feedback key '{keyword}' -> {payload}")
                return False

    def _parse_error(self, error_dict):
        """
        Parse error feedback and update the data store with an error message.

        Args:
            error_dict (dict): The error details provided by CoreMiner.

        Returns:
            bool: False, indicating that the feedback represents an error.
        """
        self.data_store.set_debuggee_output(f"CoreMiner [Error]: {error_dict}")
        return False

    def _parse_registers(self, registers_dict):
        """
        Parse and format register feedback, then update the data store.

        Each register's value is formatted as a hexadecimal string. If the register 'rip' is found, its value is also
        stored separately. The formatted registers are then saved to the data store.

        Args:
            registers_dict (dict): A dictionary with register names as keys and their values as integers.

        Returns:
            bool: True, indicating successful parsing of register feedback.
        """
        lines = []
        for reg_name, reg_value in registers_dict.items():
            lines.append(f"  {reg_name}: {reg_value:0x}")
            if reg_name == "rip":
                self.data_store.set_rip(reg_value)

        self.data_store.set_registers("\n".join(lines))
        return True

    def _parse_stack(self, stack_dict):
        """
        Parse and format the stack feedback, then update the data store.

        The method expects a starting address and a list of words. Each word is formatted into a line with its
        corresponding address (incremented by 8 for each word).

        Args:
            stack_dict (dict): A dictionary with keys "start_addr" (int) and "words" (list of ints).

        Returns:
            bool: True, indicating successful parsing of stack feedback.
        """
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
        Parse disassembly feedback and format it into a human-readable string.

        Each instruction entry is formatted into columns: address (with an optional breakpoint marker), hex bytes,
        mnemonic, and operands. The formatted disassembly is then stored in the data store.

        Args:
            disasm_dict (dict): A dictionary containing a key "vec" with a list of disassembly entries. Each entry is a list
                                containing address, a list of byte values, tokens (for mnemonic and operands), and a breakpoint flag.

        Returns:
            bool: True, indicating successful parsing of disassembly feedback.
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

            # Format address as hex and mark breakpoint if applicable
            if has_breakpoint:
                address_str = f"{address:016x}(*)"
            else:
                address_str = f"{address:016x}"
            address_col = f"{address_str:<{ADDRESS_COL_WIDTH}}"

            # Format bytes into a hex string
            byte_str = " ".join(f"{b:02x}" for b in bytes_list)
            bytes_col = f"{byte_str:<{BYTES_COL_WIDTH}}"

            # Separate the mnemonic and operand tokens
            mnemonic_text = ""
            operand_text = ""
            found_mnemonic = False
            for token in tokens:
                if token.get("kind") == "Mnemonic" and not found_mnemonic:
                    mnemonic_text = token["text"].strip()  # e.g. "mov"
                    found_mnemonic = True
                else:
                    operand_text += token["text"]

            mnemonic_col = f"{mnemonic_text:<{MNEMONIC_COL_WIDTH}}"
            operand_text = operand_text.strip()

            line_str = f"{address_col}{bytes_col}{mnemonic_col}{operand_text}"
            lines.append(line_str)

        disassembly_str = "\n".join(lines)
        self.data_store.set_disassembly(disassembly_str)
        return True

    def _parse_processmap(self, procmap_dict):
        """
        Parse process memory map feedback and format it into a detailed report.

        The method extracts summary statistics and region details (such as address range, size, offset,
        device, inode, path, and permissions) from the process map. The formatted output is stored in the data store.

        Args:
            procmap_dict (dict): A dictionary containing memory map details, including totals and a list of memory regions.

        Returns:
            bool: True, indicating successful parsing of process memory map feedback.
        """
        total_mapped = procmap_dict.get("total_mapped", 0)
        executable_regions = procmap_dict.get("executable_regions", 0)
        private_regions = procmap_dict.get("private_regions", 0)
        writable_regions = procmap_dict.get("writable_regions", 0)

        output_lines = [
            "Process Memory Map:",
            f"  Total mapped memory: {total_mapped} bytes",
            f"  Executable regions: {executable_regions}",
            f"  Writable regions: {writable_regions}",
            f"  Private regions: {private_regions}",
            "",
            "Regions:"
        ]

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

            perms = region.get("permissions", {})
            r = "r" if perms.get("read", False) else "-"
            w = "w" if perms.get("write", False) else "-"
            x = "x" if perms.get("execute", False) else "-"
            if perms.get("private", False):
                ps = "p"
            elif perms.get("shared", False):
                ps = "s"
            else:
                ps = "-"
            perm_str = r + w + x + ps

            output_lines.append(
                f"  {idx}. {path}\n"
                f"      Address Range: 0x{start_addr:016x} - 0x{end_addr:016x}\n"
                f"      Size: {size} bytes, Offset: {offset}, Device: {device}, Inode: {inode}\n"
                f"      Permissions: {perm_str}"
            )

        output = "\n".join(output_lines)
        self.data_store.set_output("CoreMiner:\n" + "ProcessMap: \n" + output)
        return True

    def _parse_backtrace(self, backtrace_dict):
        """
        Parse backtrace feedback and format it into a readable list of stack frames.

        Each frame includes the address, function name, and starting address (if available). The formatted
        backtrace is stored in the data store.

        Args:
            backtrace_dict (dict): A dictionary containing a list of frames under the key "frames".

        Returns:
            bool: True, indicating successful parsing of backtrace feedback.
        """
        frames = backtrace_dict.get("frames", [])
        output_lines = ["Backtrace:"]
        
        for idx, frame in enumerate(frames, start=1):
            addr = frame.get("addr", 0)
            name = frame.get("name") or "<unknown>"
            start_addr = frame.get("start_addr")
            addr_str = f"0x{addr:016x}"
            start_str = f"0x{start_addr:016x}" if start_addr is not None else "N/A"
            output_lines.append(f"  {idx}. Address: {addr_str} | Function: {name} | Start: {start_str}")
        
        output = "\n".join(output_lines)
        self.data_store.set_backtrace(output)
        return True

    def _parse_read_memory(self, word_value):
        """
        Parse memory read feedback by formatting a word value into hexadecimal.

        Args:
            word_value: The integer value read from memory.

        Returns:
            bool: True, indicating successful parsing of memory read feedback.
        """
        try:
            hex_word = f"0x{int(word_value):016x}"
        except (ValueError, TypeError):
            hex_word = "Invalid word value"
        
        self.data_store.set_output("CoreMiner:\n" + f"Memory word: {hex_word}")
        return True

    def _parse_symbols(self, symbols):
        """
        Parse symbols feedback and format them into a human-readable tree.

        The payload is expected to be a list of symbol dictionaries. Each symbol may have nested child symbols.
        The method recursively formats each symbol using the format_symbols helper method and stores the result.

        Args:
            symbols (list): A list of symbol dictionaries.

        Returns:
            bool: True, indicating successful parsing of symbols feedback.
        """
        output_lines = ["Symbols:"]
        for symbol in symbols:
            output_lines.extend(self.format_symbols(symbol))
            
        output = "\n".join(output_lines)
        self.data_store.set_output("CoreMiner:\n" + output)
        return True

    def format_symbols(self, symbol, indent=0):
        """
        Recursively format a symbol and its children into a list of human-readable strings.

        Args:
            symbol (dict): A dictionary representing a symbol with possible keys such as 'name', 'kind',
                           'offset', 'datatype', 'low_addr', 'high_addr', and 'children'.
            indent (int, optional): The current indentation level for nested symbols. Defaults to 0.

        Returns:
            list: A list of formatted strings representing the symbol and its children.
        """
        indent_str = "  " * indent
        name = symbol.get("name") if symbol.get("name") is not None else "<anonymous>"
        kind = symbol.get("kind", "<unknown>")
        offset = symbol.get("offset")
        datatype = symbol.get("datatype")
        low_addr = symbol.get("low_addr")
        high_addr = symbol.get("high_addr")

        line = f"{indent_str}{kind}: {name}"
        if offset is not None:
            line += f", offset: {offset}"
        if datatype is not None:
            line += f", datatype: {datatype}"
        if low_addr is not None or high_addr is not None:
            low_str = f"0x{low_addr:016x}" if low_addr is not None else "?"
            high_str = f"0x{high_addr:016x}" if high_addr is not None else "?"
            line += f", range: {low_str} - {high_str}"

        lines = [line]
        for child in symbol.get("children", []):
            lines.extend(self.format_symbols(child, indent=indent + 1))
        return lines

    def _parse_variable(self, variable_dict):
        """
        Parse variable feedback by formatting its byte values into a hexadecimal string.

        The payload is expected to be a dictionary with a key 'Bytes' that contains a list of integers.
        The formatted variable value is then stored in the data store.

        Args:
            variable_dict (dict): A dictionary containing variable data with a 'Bytes' key.

        Returns:
            bool: True, indicating successful parsing of variable feedback.
        """
        bytes_list = variable_dict.get("Bytes", [])
        hex_bytes = " ".join(f"{b:02x}" for b in bytes_list)
        output = f"Variable: {hex_bytes}"
        self.data_store.set_output("CoreMiner:\n" + output)
        return True

    def _parse_plugin_list(self, plugin_list_payload):
        """
        Parse plugin list feedback and format it for display.

        The payload is expected to be a list of pairs, each containing a plugin name and its activation status.
        The formatted list is stored in the data store.

        Args:
            plugin_list_payload (list): A list where each element is a pair [plugin_name, active].

        Returns:
            bool: True, indicating successful parsing of plugin list feedback.
        """
        output_lines = ["   Plugins:"]
        for entry in plugin_list_payload:
            if isinstance(entry, list) and len(entry) == 2:
                plugin_name, active = entry
                status = "activated" if active else "deactivated"
                output_lines.append(f"      - {plugin_name}: {status}")
            else:
                output_lines.append(f"      - Invalid entry: {entry}")
        output = "\n".join(output_lines)
        self.data_store.set_output("CoreMiner:\n" + output)
        return True
