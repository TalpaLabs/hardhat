<div align="center">
    <h1>HardHat</h1>
    <h3>🔩 HardHat 👷</h3>
    <p>
        A textual user interface for Coreminer
    </p>
    <br/>
    <a href="https://python.org">
        <img src="https://img.shields.io/badge/language-Python-blue.svg" alt="Python"/>
    </a>
    <a href="https://github.com/TalpaLabs/coreminer">
        <img src="https://img.shields.io/badge/Requires-Coreminer-red.svg" alt="Requires Coreminer"/>
    </a>
    <a href="https://github.com/TalpaLabs/hardhat/blob/master/LICENSE">
        <img src="https://img.shields.io/github/license/TalpaLabs/hardhat" alt="License"/>
    </a>
    <a href="https://github.com/TalpaLabs/hardhat/releases">
        <img src="https://img.shields.io/github/v/release/TalpaLabs/hardhat" alt="Release"/>
    </a>
</div>

# HardHat

HardHat is a powerful Textual User Interface (TUI) for the [Coreminer](https://github.com/TalpaLabs/coreminer) debugger. It provides an intuitive, terminal-based interface that enhances the debugging experience with Coreminer while maintaining the flexibility and power of the command-line.

## Features

- **Customizable multi-pane interface**: Arrange different views to suit your debugging workflow
- **Richer command input**: Command history navigation
- **Multiple data views**:
  - **Disassembly view**: Code disassembly with breakpoint indicators
  - **Register view**: CPU register values
  - **Stack view**: Current stack contents
  - **Output view**: Program and debugger output
  - **Backtrace view**: Current backtrace
  - **Raw responses**: Full JSON data for debugging the debugger itself
- **Plugin management**: Enable/disable Coreminer plugins directly from the UI
- **Keyboard navigation**: Efficient workflow with keyboard shortcuts

## Requirements

- Python 3.13+
- [Coreminer](https://github.com/TalpaLabs/coreminer) debugger with the `cmserve` binary, at least v0.4.0
- [Textual](https://textual.textualize.io/getting_started/#installation) library

## Installation

### Install Coreminer

HardHat requires the Coreminer debugger to be installed. Follow the Coreminer installation instructions from its [README](https://github.com/TalpaLabs/coreminer/blob/master/README.md).

Ensure that `cmserve` is in your PATH after installing Coreminer.

### Install HardHat

```bash
# Clone the repository
git clone https://github.com/TalpaLabs/hardhat.git
cd hardhat

# Install dependencies
pip install -e .

# For development
pip install -e ".[dev]"
```

## Usage

### Launch HardHat

```bash
python src/app.py
```

### Basic Interface

HardHat provides four customizable window panes that can display different widgets:

- Main window (large)
- Two small windows
- Medium window
- Command input at the bottom

Click the [+] tab in any window to add a widget:

- **Output**: Program and debugger output
- **Disassembly**: Disassembled code view
- **Registers**: CPU register values
- **Stack**: Current stack values
- **RawResponses**: Raw JSON responses from Coreminer

### Commands

HardHat supports all Coreminer commands with a similar syntax. Here are some examples:

```
# Run a program
run /path/to/executable arg1 arg2

# Set a breakpoint at an address
bp 0x4000000

# Delete a breakpoint
dbp 0x4000000

# Continue execution
c

# Step instructions
s                  # Single step
si                 # Step into function
so                 # Step out of function
sov                # Step over function

# View memory and registers
d 0x4000000 20     # Disassemble 20 bytes at address
regs get           # View registers
stack              # View stack
bt                 # View backtrace
pm                 # View process memory map

# Memory operations
rmem 0x7fffffffe000  # Read word at address
wmem 0x7fffffffe000 0x1234  # Write word to address

# View symbols and variables
sym main           # Look up symbol 'main'
var count          # View variable value
vars count 42      # Set variable value

# Plugin management
plugins            # List all plugins
plugin sigtrap_guard true  # Enable a plugin
```

Press CTRL + P to open the command palette and click "Help Menu" to see all available commands.

## Architecture

HardHat uses a MVC-inspired architecture:

- **Data Store**: Central repository for application state
- **Feedback Parser**: Processes JSON responses from Coreminer
- **Command Parser**: Converts user commands to Coreminer JSON requests
- **Coreminer Interface**: Manages communication with the Coreminer process
- **UI Components**: Textual widgets for displaying different views

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: Add some amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

Note: this project makes use of [conventional git commits](https://www.conventionalcommits.org/en/v1.0.0/).

## License

Distributed under the MIT License. See the LICENSE file for more information.

## Acknowledgements

- [Coreminer](https://github.com/TalpaLabs/coreminer) - The debugger powering HardHat
- [Textual](https://github.com/Textualize/textual) - The TUI framework used to build HardHat
