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
            "quit"              : self.handle_quit,
            "exit"              : self.handle_quit,
            "q"                 : self.handle_quit,
        }

    def get_help_text(self):
        return self.help_text

    def parse(self, input_string: str):
        tokens = shlex.split(input_string)

        for i, token in enumerate(tokens):
            if token.startswith("0x"):
                try:
                    tokens[i] = str(int(token, 16))
                except ValueError:
                    pass

        # 2) Parse with your argparse parser
        try:
            args = self.parser.parse_args(tokens)
        except SystemExit:
            result_dict = {
                "feedback": {
                    "Error": {
                        "error_type": "command",
                        "message": f"Unknown command: {input_string}"
                    }
                }
            }
            return result_dict

        handler = self.command_handlers.get(args.command, self.handle_unknown)
        return handler(args)
    
    def handle_procmap(self, args):
        return {"status": "ProcMap"}
    
    def handle_backtarce(self, args):
        return {"status": "BackTrace"}
    
    def handle_continue(self, args):
        return {"status": "Continue"}
    
    def handle_step_over(self, args):
        return {"status": "StepOver"}
    
    def handle_step_out(self, args):
        return {"status": "StepOut"}
    
    def handle_step_into(self, args):
        return {"status": "StepInto"}
    
    def handle_step_single(self, args):
        return {"status": "StepSingle"}
    
    def handle_get_stack(self, args):
        return {"status": "GetStack"}
    
    def handle_quit(self, args):
        # Todo 
        return {"status": "DebuggerQuit"}
    
    # No subcommand matched
    def handle_unknown(self, args):
        result_dict = {
            "feedback": {
                "Error": {
                    "error_type": "command",
                    "message": f"Unknown command: {args.command}"
                }
            }
        }
        return result_dict