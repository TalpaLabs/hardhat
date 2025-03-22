from textual.app import App, ComposeResult, SystemCommand
from textual.screen import Screen
from typing import Iterable
from views.help_menu import HelpMenu
from views.main_view import MainView

class HardHat(App):
    """
    Main Textual application class for HardHat.

    This class initializes the application by pushing the main view screen upon mounting.
    It also extends the system command palette with a custom command to open the help screen.

    Methods:
        on_mount(): Called when the application is mounted to the screen; it pushes the main view.
        get_system_commands(screen: Screen) -> Iterable[SystemCommand]:
            Yields both default and custom system commands for the current screen.
        show_commands_help():
            Handler for the custom "Help Menue" command that opens the help screen.
    """
    
    def on_mount(self):
        """
        Called when the application is mounted.

        This method pushes the main view screen (MainView) onto the screen stack to initialize the user interface.
        """
        self.push_screen(MainView())

    def get_system_commands(self, screen: Screen) -> Iterable[SystemCommand]:
        """
        Extend the system command palette with custom commands.

        This method yields the default system commands from the parent class and adds a custom command:
        "Help Menue", which opens the HardHat help screen when invoked.

        Args:
            screen (Screen): The current screen context for which system commands are being generated.

        Returns:
            Iterable[SystemCommand]: An iterable of system commands including both default and custom commands.
        """
        # Include default commands
        yield from super().get_system_commands(screen)

        # Add our own custom command
        yield SystemCommand(
            "Help Menue",
            "Open HardHat usage / help screen",
            self.show_commands_help,
        )

    def show_commands_help(self) -> None:
        """
        Open the HardHat help screen.

        This method is called by the custom "Help Menue" system command.
        It pushes the HelpMenu modal screen onto the screen stack to display usage instructions and help information.
        """
        self.push_screen(HelpMenu())

if __name__ == "__main__":
    HardHat().run()
