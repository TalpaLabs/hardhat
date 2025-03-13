
import json
import shlex

def parse_command_logic(command: str):
        """
        Turn a user-typed command like:
        "SetBreakPoint 0xDEADBEEF"
        into JSON like:
        {"status": {"SetBreakPoint": 3735928559}}
        """
        tokens = shlex.split(command)
        if not tokens:
            return ""

        cmd = tokens[0].lower()
        args = tokens[1:]

        # Dispatch table: command -> function returning a dict
        command_table = {
            # Single-word commands
            "procmap":       lambda args: {"status": "ProcMap"},
            "pm":            lambda args: {"status": "ProcMap"},

            "backtrace":     lambda args: {"status": "Backtrace"},
            "bt":            lambda args: {"status": "Backtrace"},

            "continue":      lambda args: {"status": "Continue"},
            "cont":          lambda args: {"status": "Continue"},
            "c":             lambda args: {"status": "Continue"},

            "stepover":      lambda args: {"status": "StepOver"},
            "sov":           lambda args: {"status": "StepOver"},

            "stepout":       lambda args: {"status": "StepOut"},
            "so":            lambda args: {"status": "StepOut"},

            "stepinto":      lambda args: {"status": "StepInto"},
            "si":            lambda args: {"status": "StepInto"},

            "stepsingle":    lambda args: {"status": "StepSingle"},
            "step":          lambda args: {"status": "StepSingle"},
            "s":             lambda args: {"status": "StepSingle"},

            "getstack":      lambda args: {"status": "GetStack"},
            "stack":         lambda args: {"status": "GetStack"},

            "debuggerquit":  lambda args: {"status": "DebuggerQuit"},
            "quit":          lambda args: {"status": "DebuggerQuit"},
            "exit":          lambda args: {"status": "DebuggerQuit"},
            "q":             lambda args: {"status": "DebuggerQuit"},

            "info":          lambda args: {"status": "Infos"},

            # Complex commands
            "run":           parse_run,
            # "setbreakpoint": parse_setbreakpoint, ...
        }

        if cmd not in command_table:
            # Unknown command: queue an error and exit
            result_dict = {
                "feedback": {
                    "Error": {
                        "error_type": "command",
                        "message": f"Unknown command: {cmd} {args}"
                    }
                }
            }
            return result_dict

        # Call the parser function to build a dict
        parse_func = command_table[cmd]
        result_dict = parse_func(args)

        return result_dict

def parse_run(args: list[str]) -> dict:
    """
    "Run /bin/ls -la" -> 
    {"status": {"Run": ["/bin/ls", [ [47,101,116,99], [45,108,97] ] ]}}
    """
    if not args:
        result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Missing Arguments run PATH [ARGS]"}}
        }
        return result_dict

    path = args[0]
    rest = args[1:] 

    return {"status": {"Run": [path, rest]}}