"""
Module for parsing and handling debugger commands in the HardHat application.

This module defines the CommandParser class, which leverages the argparse module to create
a command-line interface for various debugger operations. It maps commands (and their aliases)
to corresponding handler functions that return the appropriate status messages and flags.
Additionally, the module provides a helper function, str2bool, for converting string inputs
to boolean values.
"""

import argparse
import shlex
import subprocess


class CommandParser():
    """
    A command parser for the HardHat debugger application.

    This class sets up an argparse-based parser with subcommands for various debugging operations,
    such as viewing the process map, backtrace, controlling execution, managing breakpoints,
    reading/writing memory, manipulating registers, disassembly, variable access, and plugin management.
    It also maintains a mapping between command names (including aliases) and their corresponding
    handler methods.
    """

    def __init__(self):
        """
        Initialize the CommandParser.

        Creates the main argument parser and configures subparsers for each supported command,
        along with their arguments and help messages. Also, stores the formatted help text and
        sets up a dictionary mapping command names to their respective handler methods.
        """

        # Create the main (top-level) parser
        self.parser = argparse.ArgumentParser(prog="HardHat")

        # Create a subparsers object which will hold each sub-command
        subparsers = self.parser.add_subparsers(dest="command")

        # ProcMap
        procmap_parser = subparsers.add_parser(
            "procmap", aliases=["pm"], help="Shows the ProcMap")

        # Backtrace
        backtrace_parser = subparsers.add_parser(
            "backtrace", aliases=["bt"], help="Gets the Backtrace")

        # Continue
        continue_parser = subparsers.add_parser(
            "continue", aliases=["cont", "c"], help="Continues debuggee")

        # Step over
        step_over_parser = subparsers.add_parser(
            "stepover", aliases=["sov"], help="Performs step over")

        # Step out
        step_out_parser = subparsers.add_parser(
            "stepout", aliases=["so"], help="Performs step out")

        # Step into
        step_into_parser = subparsers.add_parser(
            "stepinto", aliases=["si"], help="Performs step into")

        # Step single
        step_single_parser = subparsers.add_parser(
            "step", aliases=["s"], help="Performs single step")

        # Get Stack
        get_stack_parser = subparsers.add_parser(
            "stack", aliases=[], help="Gets the current stack")

        # Get version
        version_parser = subparsers.add_parser(
            "version", aliases=[], help="Gets metadata about hardhat and coreminer")

        # Quit
        # quit_parser = subparsers.add_parser("quit", aliases=["exit", "q"], help="Quits HardHat")

        # Run
        run_parser = subparsers.add_parser(
            "run", aliases=[], help="Runs debugee")
        run_parser.add_argument(
            "path", type=str, help="path to the binary you want to debugg")
        run_parser.add_argument(
            "options", nargs="*", help="Optional arguments for running the binary")

        # Set breakepoint
        set_breakpoint_parser = subparsers.add_parser(
            "break", aliases=["bp"], help="Set a breakpoint")
        set_breakpoint_parser.add_argument(
            "addr", type=parse_hex, help="address where to set the breakpoint")

        # Del breakepoint
        set_breakpoint_parser = subparsers.add_parser(
            "delbreak", aliases=["dbp"], help="Deletes a breakpoint")
        set_breakpoint_parser.add_argument(
            "addr", type=parse_hex, help="address where to delete the breakpoint")

        # Read memory
        read_memory_parser = subparsers.add_parser(
            "rmem", aliases=[], help="Read a word at addr")
        read_memory_parser.add_argument(
            "addr", type=parse_hex, help="address where you want to read a word")

        # Write memory
        write_memory_parser = subparsers.add_parser(
            "wmem", aliases=[], help="Write a word at addr")
        write_memory_parser.add_argument(
            "addr", type=parse_hex, help="address where you want to write a word")
        write_memory_parser.add_argument(
            "value", type=parse_hex, help="value you want to write")

        # Get & Set regs
        get_set_regs_parser = subparsers.add_parser(
            "regs", aliases=[], help="Do somethig with registers")
        get_set_regs_parser.add_argument(
            "action", choices=["get", "set"], help="get all registers or set one")
        get_set_regs_parser.add_argument(
            "options", nargs="*", help="Optional arguments for running the binary")

        # Get Symbol
        get_symbol_parser = subparsers.add_parser(
            "sym", aliases=["gsym"], help="Get a symbol by name")
        get_symbol_parser.add_argument(
            "name", type=str, help="name of the symbol")

        # Get Disassembly
        get_disassembly_parser = subparsers.add_parser(
            "dis", aliases=["d"], help="Disassemble at address")
        get_disassembly_parser.add_argument(
            "addr", type=parse_hex, help="address where you want to disassemble")
        get_disassembly_parser.add_argument(
            "length", type=parse_hex, help="bytes you want to disassemble")

        # Set variable
        set_variable_parser = subparsers.add_parser(
            "vars", aliases=[], help="Set a variable by name")
        set_variable_parser.add_argument(
            "name", type=str, help="name of the variable")
        set_variable_parser.add_argument(
            "value", type=parse_hex, help="value to set to")

        # Get variable
        get_variable_parser = subparsers.add_parser(
            "var", aliases=[], help="Get a variable by name")
        get_variable_parser.add_argument(
            "name", type=str, help="name of the variable")

        # Get plugins
        get_plugins_parser = subparsers.add_parser(
            "plugins", aliases=[], help="Get all available plugins")

        # Enable & disable plugins
        enable_disable_plugin_parser = subparsers.add_parser(
            "plugin", aliases=[], help="Enable or disable plugins")
        enable_disable_plugin_parser.add_argument(
            "name", type=str, help="name of the plugin")
        enable_disable_plugin_parser.add_argument(
            "value", type=str2bool, help="bool to activate or disable plugin")

        self.help_text = self.parser.format_help()

        self.command_handlers = {
            "procmap": self.handle_procmap,
            "pm": self.handle_procmap,
            "backtrace": self.handle_backtarce,
            "bt": self.handle_backtarce,
            "continue": self.handle_continue,
            "cont": self.handle_continue,
            "c": self.handle_continue,
            "stepover": self.handle_step_over,
            "sov": self.handle_step_over,
            "stepout": self.handle_step_out,
            "so": self.handle_step_out,
            "stepinto": self.handle_step_into,
            "si": self.handle_step_into,
            "stepsingle": self.handle_step_single,
            "step": self.handle_step_single,
            "s": self.handle_step_single,
            "getstack": self.handle_get_stack,
            "stack": self.handle_get_stack,
            # "quit"              : self.handle_quit,
            # "exit"              : self.handle_quit,
            # "q"                 : self.handle_quit,
            "run": self.handle_run,
            "setbreakpoint": self.handle_set_breakpoint,
            "break": self.handle_set_breakpoint,
            "bp": self.handle_set_breakpoint,
            "delbreakpoint": self.handle_delete_breakpoint,
            "delbreak": self.handle_delete_breakpoint,
            "dbp": self.handle_delete_breakpoint,
            "rmem": self.handle_read_memory,
            "wmem": self.handle_write_memory,
            "regs": self.handle_get_set_registers,
            "sym": self.handle_get_symbol,
            "gsym": self.handle_get_symbol,
            "dis": self.handle_get_disassembly,
            "d": self.handle_get_disassembly,
            "vars": self.handle_set_variable,
            "var": self.handle_get_variable,
            "plugins": self.handle_get_plugins,
            "plugin": self.handle_enable_disable_plugin,
            "version": self.handle_version
        }

    def get_help_text(self):
        return self.help_text

    def parse(self, input_string: str):
        """
        Parse an input command string and dispatch it to the appropriate handler.

        This method tokenizes the input string, attempts to convert tokens (except the command itself)
        from hexadecimal to decimal when applicable, and parses the tokens using argparse. If the parsing
        fails due to an unknown command, it returns an error feedback. Otherwise, the method calls the
        associated command handler and returns its result.

        Args:
            input_string (str): The raw command string entered by the user.

        Returns:
            tuple: A tuple containing a dictionary with the command status or error feedback, and a boolean
                   flag indicating whether basic information need to be updated like register or the stack.
        """
        tokens = shlex.split(input_string)

        try:
            args, optional_args = self.parser.parse_known_args(tokens)
        except SystemExit:
            result_dict = ({
                "feedback": {
                    "Error": {
                        "error_type": "command",
                        "message": f"Unknown command: {input_string}"
                    }
                }
            }, False)
            return result_dict

        handler = self.command_handlers.get(args.command, self.handle_unknown)
        return handler(args, optional_args)

    def handle_procmap(self, args, optional_args):
        return ({"status": "ProcMap"}, False)

    def handle_backtarce(self, args, optional_args):
        return ({"status": "Backtrace"}, False)

    def handle_continue(self, args, optional_args):
        return ({"status": "Continue"}, True)

    def handle_step_over(self, args, optional_args):
        return ({"status": "StepOver"}, True)

    def handle_step_out(self, args, optional_args):
        return ({"status": "StepOut"}, True)

    def handle_step_into(self, args, optional_args):
        return ({"status": "StepInto"}, True)

    def handle_step_single(self, args, optional_args):
        return ({"status": "StepSingle"}, True)

    def handle_get_stack(self, args, optional_args):
        return ({"status": "GetStack"}, False)

    # def handle_quit(self, args, optional_args):
    #    return ({"status": "DebuggerQuit"}, False)

    def handle_run(self, args, optional_args):
        optional_args = []
        for arg in args.options:
            optional_args.append(f"{arg}")
        for arg in optional_args:
            optional_args.append(f"{arg}")
        return ({"status": {"Run": [f"{args.path}", optional_args]}}, True)

    def handle_set_breakpoint(self, args, optional_args):
        return ({"status": {"SetBreakpoint": args.addr}}, True)

    def handle_delete_breakpoint(self, args, optional_args):
        return ({"status": {"DelBreakpoint": args.addr}}, True)

    def handle_read_memory(self, args, optional_args):
        return ({"status": {"ReadMem": args.addr}}, False)

    def handle_write_memory(self, args, optional_args):
        return ({"status": {"WriteMem": [args.addr, args.value]}}, True)

    def handle_get_set_registers(self, args, optional_args):
        if args.action == "get":
            return ({"status": "DumpRegisters"}, False)
        else:
            if len(args.options) == 2:
                try:
                    return ({"status": {"SetRegister": [args.options[0], args.options[1]]}}, True)
                except ValueError:
                    pass
            return self.handle_unknown(args, optional_args)

    def handle_get_symbol(self, args, optional_args):
        return ({"status": {"GetSymbolsByName": args.name}}, False)

    def handle_get_disassembly(self, args, optional_args):
        return ({"status": {"DisassembleAt": [args.addr, args.length, False]}}, False)

    def handle_get_variable(self, args, optional_args):
        return ({"status": {"ReadVariable": args.name}}, False)

    def handle_set_variable(self, args, optional_args):
        return ({"status": {"ReadVariable": [args.name, args.value]}}, True)

    def handle_get_plugins(self, args, optional_args):
        return ({"status": "PluginGetList"}, False)

    def handle_enable_disable_plugin(self, args, optional_args):
        return ({"status": {"PluginSetEnable": [args.name, args.value]}}, False)

    def handle_version(self, args, optional_args):
        result_dict = ({
            "feedback": {
                "version": subprocess.check_output(["cmserve", "--version"])
                .decode("utf-8")
            }}, False)
        return result_dict

    # No subcommand matched

    def handle_unknown(self, args, optional_args):
        result_dict = ({
            "feedback": {
                "Error": {
                    "error_type": "command",
                    "message": f"Unknown command: {args.command}"
                }
            }
        }, False)
        return result_dict


def str2bool(value: str) -> bool:
    """
    Convert a string to a boolean.
    Accepts 'true', '1', 'false', '0' (case-insensitive).
    Raises an error if the string is not recognized.
    """
    value_lower = value.lower()
    if value_lower in ('true', '1', 'activate'):
        return True
    elif value_lower in ('false', '0', 'deactivate'):
        return False
    else:
        raise argparse.ArgumentTypeError(
            "Boolean value expected. Use 'true', 'false', '1', or '0'.")


def parse_hex(input: str) -> int:
    # TODO: strip 0x prefix
    return int(input, 16)
