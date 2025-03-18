import argparse
import shlex

class CommandParser():
   
    def __init__(self):
        # Create the main (top-level) parser
        self.parser = argparse.ArgumentParser(prog="HardHat")

        # Create a subparsers object which will hold each sub-command
        subparsers = self.parser.add_subparsers(dest="command")

        # ProcMap
        procmap_parser = subparsers.add_parser("procmap", aliases=["pm"], help="Shows the ProcMap")

        # Backtrace
        backtrace_parser = subparsers.add_parser("backtrace", aliases=["bt"], help="Gets the Backtrace")

        # Continue
        continue_parser = subparsers.add_parser("continue", aliases=["cont", "c"], help="Continues debuggee")

        # Step over
        step_over_parser = subparsers.add_parser("stepover", aliases=["sov"], help="Performs step over")

        # Step out
        step_out_parser = subparsers.add_parser("stepout", aliases=["so"], help="Performs step out")

        # Step into
        step_into_parser = subparsers.add_parser("stepinto", aliases=["si"], help="Performs step into")

        # Step single
        step_single_parser = subparsers.add_parser("steepsingle", aliases=["step", "s"], help="Performs single step")

        # Get Stack
        get_stack_parser = subparsers.add_parser("getstack", aliases=["stack"], help="Gets the current stack")

        # Quit
        quit_parser = subparsers.add_parser("quit", aliases=["exit", "q"], help="Quits HardHat")

        # Run
        run_parser = subparsers.add_parser("run", aliases=[], help="Runs debugee")
        run_parser.add_argument("path", type=str, help="path to the binary you want to debugg")
        run_parser.add_argument("options", nargs="*", help="Optional arguments for running the binary")

        # Set breakepoint
        set_breakpoint_parser = subparsers.add_parser("setbreakpoint", aliases=["break", "bp"], help="Set a breakpoint")
        set_breakpoint_parser.add_argument("addr", type=int, help="address where to set the breakpoint")

        # Del breakepoint
        set_breakpoint_parser = subparsers.add_parser("delbreakpoint", aliases=["delbreak", "dbp"], help="Deletes a breakpoint")
        set_breakpoint_parser.add_argument("addr", type=int, help="address where to delete the breakpoint")

        # Read memory
        read_memory_parser = subparsers.add_parser("rmem", aliases=[], help="Read a word at addr")
        read_memory_parser.add_argument("addr", type=int, help="address where you want to read a word")

        # Write memory
        write_memory_parser = subparsers.add_parser("wmem", aliases=[], help="Write a word at addr")
        write_memory_parser.add_argument("addr", type=int, help="address where you want to write a word")
        write_memory_parser.add_argument("value", type=int, help="value you want to write")

        # Get & Set regs 
        get_set_regs_parser = subparsers.add_parser("regs", aliases=[], help="Do somethig with registers")
        get_set_regs_parser.add_argument("action", choices=["get", "set"], help="get all registers or set one")
        get_set_regs_parser.add_argument("options", nargs="*", help="Optional arguments for running the binary")

        # Get Symbol
        get_symbol_parser = subparsers.add_parser("sym", aliases=["gsym"], help="Get a symbol by name")
        get_symbol_parser.add_argument("name", type=str, help="name of the symbol")

        # Get Disassembly
        get_disassembly_parser = subparsers.add_parser("dis", aliases=["d"], help="Disassemble at address")
        get_disassembly_parser.add_argument("addr", type=int, help="address where you want to disassemble")
        get_disassembly_parser.add_argument("length", type=int, help="bytes you want to disassemble")

        # Set variable
        set_variable_parser = subparsers.add_parser("vars", aliases=[], help="Set a variable by name")
        set_variable_parser.add_argument("name", type=str, help="name of the variable")
        set_variable_parser.add_argument("value", type=int, help="value to set to")

        # Get variable
        get_variable_parser = subparsers.add_parser("var", aliases=[], help="Get a variable by name")
        get_variable_parser.add_argument("name", type=str, help="name of the variable")

        self.help_text = self.parser.format_help()

        self.command_handlers = {
            "procmap"           : self.handle_procmap,
            "pm"                : self.handle_procmap,
            "backtrace"         : self.handle_backtarce,
            "bt"                : self.handle_backtarce,
            "continue"          : self.handle_continue,
            "cont"              : self.handle_continue,
            "c"                 : self.handle_continue,
            "stepover"          : self.handle_step_over,
            "sov"               : self.handle_step_over,
            "stepout"           : self.handle_step_out,
            "so"                : self.handle_step_out,
            "stepinto"          : self.handle_step_into,
            "si"                : self.handle_step_into,
            "stepsingle"        : self.handle_step_single,
            "step"              : self.handle_step_single,
            "s"                 : self.handle_step_single,
            "getstack"          : self.handle_get_stack,
            "stack"             : self.handle_get_stack,
            "quit"              : self.handle_quit,
            "exit"              : self.handle_quit,
            "q"                 : self.handle_quit,
            "run"               : self.handle_run,
            "setbreakpoint"     : self.handle_set_breakpoint,
            "break"             : self.handle_set_breakpoint,
            "bp"                : self.handle_set_breakpoint,
            "delbreakpoint"     : self.handle_delete_breakpoint,
            "delbreak"          : self.handle_delete_breakpoint,
            "dbp"               : self.handle_delete_breakpoint,
            "rmem"              : self.handle_read_memory,
            "wmem"              : self.handle_write_memory,
            "regs"              : self.handle_get_set_registers,
            "sym"               : self.handle_get_symbol,
            "gsym"              : self.handle_get_symbol,
            "dis"               : self.handle_get_disassembly,
            "d"                 : self.handle_get_disassembly,
            "vars"              : self.handle_set_variable,
            "var"               : self.handle_get_variable,
        }

    def get_help_text(self):
        return self.help_text

    def parse(self, input_string: str):
        tokens = shlex.split(input_string)

        for i, token in enumerate(tokens[1:], start=1):
            try:
                tokens[i] = str(int(token, 16))
            except ValueError:
                pass
        
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
        return ({"status": "BackTrace"}, False)
    
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
    
    def handle_quit(self, args, optional_args):
        # Todo 
        return ({"status": "DebuggerQuit"}, False)
    
    def handle_run(self, args, optional_args):
        byte_args = []
        for arg in optional_args:
            byte_args.append([b for b in arg.encode("utf-8")])
        return ({"status": {"Run": [args.path, byte_args]}}, True)
    
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
                    return ({"status": {"SetRegister": [args.options[0], int(args.options[1])]}}, True)
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