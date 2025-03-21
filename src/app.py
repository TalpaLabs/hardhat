from textual.app import App, ComposeResult, SystemCommand
from textual.screen import Screen
from typing import Iterable
from views.help_menu import HelpMenu
from views.main_view import MainView

class HardHat(App):
    """Main Textual application."""
    def on_mount(self):
        self.push_screen(MainView())

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """
        Add our custom "help menue" system command to the palette.
        """
        # Include default commands
        yield from super().get_system_commands(screen)

        # Add our own command
        yield SystemCommand(
            "Help Menue",
            "Open HardHat usage / help screen",
            self.show_commands_help,
        )

    def show_commands_help(self) -> None:
        """Method called by the 'Help Menue' command."""
        self.push_screen(HelpMenu())

if __name__ == "__main__":
    HardHat().run()