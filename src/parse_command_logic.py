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

        for i, arg in enumerate(args):
            if arg.startswith("0x"):
                try:
                    args[i] = int(arg, 16)
                except ValueError:
                    pass

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

            #"info":          lambda args: {"status": "Infos"},

            # Complex commands
            "run":           parse_run,

            "setbreakpoint": parse_setbreakpoint,
            "bp":            parse_setbreakpoint,

            "readmemory":    parse_readmemory,
            "readmem":       parse_readmemory,
            "rmem":          parse_readmemory,

            "writememory":   parse_writememory,
            "writemem":      parse_writememory,
            "wmem":          parse_writememory,

            "registers":      parse_registers,
            "regs":           parse_registers,
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
    "Run /bin/ls /etc -la" -> 
    {"status": {"Run": ["/bin/ls", [ [47,101,116,99], [45,108,97] ] ]}}
    """
    if not args:
        result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Missing arguments - run PATH [ARGS]"}}
        }
        return result_dict

    path = args[0]
    extras = args[1:] 

    byte_args = []
    for arg in extras:
        byte_args.append([b for b in arg.encode("utf-8")])

    return {"status": {"Run": [path, byte_args]}}

def parse_setbreakpoint(args: list[str]):
    if len(args) != 1:
        result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Wrong argument number - bp ADDR"}}
        }
        return result_dict
    
    try:
        address = int(args[0])
    except:
        result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Wrong argument number - bp ADDR"}}
        }
        return result_dict
    return {"status": {"SetBreakpoint": int(address)}}

def parse_readmemory(args: list[str]):
    if len(args) != 1:
        result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Invallid argument type - rmem ADDR"}}
        }
        return result_dict
    try:
        address = int(args[0])
    except:
        result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Wrong argument type - rmem ADDR"}}
        }
        return result_dict
    return {"status": {"ReadMem": int(address)}}

def parse_writememory(args: list[str]):
    if len(args) != 2:
        result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Wrong argument number - wmem ADDR VAL"}}
        }
        return result_dict
    try:
        address = int(args[0])
        value = int(args[1])
    except:
        result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Invalid argument type - wmem ADDR VAL"}}
        }
        return result_dict
    return {"status": {"WriteMem": [int(address), int(value)]}}

def parse_registers(args: list[str]):

    if len(args) == 1:
        if args[0] == "get":
            return {"status": "DumpRegisters"}
        else:
            result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Unknown argument! Did you mean 'regs get' or 'regs set REG VALUE'"}}
            }
            return result_dict
    elif len(args) == 3:
        if args[0] == "set":
            try:
                name = args[0]
                value = int(args[1])
            except:
                result_dict = {
                "feedback": {"Error":{"error_type": "command", "message": "Invalid argument type - wmem ADDR VAL"}}
                }
                return result_dict
            return {"status": {"SetRegister": [name, value]}}
        else:
            result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Unknown argument! Did you mean 'regs get' or 'regs set REG VALUE'"}}
            }
            return result_dict
    else:
        result_dict = {
            "feedback": {"Error":{"error_type": "command", "message": "Wrong argument number - regs get - regs set REG VALUE"}}
        }
        return result_dict