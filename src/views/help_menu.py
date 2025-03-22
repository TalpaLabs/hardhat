from textual.screen import ModalScreen
from textual.app import ComposeResult
from textual.containers import Grid, ScrollableContainer, VerticalScroll
from textual.widgets import Button, Static

class HelpMenu(ModalScreen[str]):
    """Modal popup for showing the help menu."""
    
    CSS_PATH = "../css/help_menu.tcss"

    USAGE_TEXT = """
    run PATH \[ARGS]         - Run program at PATH with optional arguments
    c, cont                 - Continue execution
    s, step                 - Step one instruction
    si                      - Step into function call
    su, sov                 - Step over function call
    so                      - Step out of current function
    bp, break ADDR          - Set breakpoint at address (hex)
    dbp, delbreak ADDR      - Delete breakpoint at address (hex)
    d, dis ADDR LEN         - Disassemble LEN bytes at ADDR
    bt                      - Show backtrace
    stack                   - Show stack
    pm                      - Show process memory map
    regs get                - Show register values
    regs set REG VAL        - Set register REG to value VAL (hex)
    rmem ADDR               - Read memory at address (hex)
    wmem ADDR VAL           - Write value to memory at address (hex)
    sym, gsym NAME          - Look up symbol by name
    var NAME                - Read variable value
    vars NAME VAL           - Write value to variable
    plugins                 - Get a List of all available plugins
    plugin NAME BOOL        - Activate or deactivate a plugin
    """

    def compose(self) -> ComposeResult:
        # You can layout your widgets however you like
        yield Grid(
            Static("Help Menu:", id="selector_title"),
            ScrollableContainer(
                VerticalScroll(
                    Static(self.USAGE_TEXT, id="help_text")
                ),
                id="scroll_container",
            ),
            Button("Close", variant="primary", id="close_button"),
            id="dialog"
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "close_button":
            self.app.pop_screen()