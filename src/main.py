"""Module with application's window"""
from .window import Texty2Window
import sys
import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Gio, Adw

class Texty2Application(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='ca.footeware.py.texty2',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        # Keyboard Shortcuts dialog
        builder = Gtk.Builder()
        builder.add_from_resource('/ca/footeware/py/texty2/help_overlay.ui')
        self.shortcuts_window = builder.get_object("help-overlay")

        # Keyboard Shortcuts action
        keyboard_shortcuts_action = Gio.SimpleAction.new("keyboard-shortcuts", None)
        keyboard_shortcuts_action.connect("activate", self.on_keyboard_shortcuts_action)
        self.add_action(keyboard_shortcuts_action)
        self.set_accels_for_action("app.keyboard-shortcuts", ["<primary>question"])

        # About action
        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.on_about_action)
        self.add_action(about_action)

        # New window action
        new_window_action = Gio.SimpleAction.new("new-window", None)
        new_window_action.connect("activate", self.on_new_window_action)
        self.add_action(new_window_action)
        self.set_accels_for_action("app.new-window", ['<primary><shift>n'])

    def do_activate(self):
        """Create a new window if there are no windows."""
        if not self.get_windows():
            self.on_new_window_action(None, None)

    def on_new_window_action(self, action, parameter):
        """Handle the New Window menu button being clicked."""
        win = Texty2Window(application=self)
        win.present()

    def on_keyboard_shortcuts_action(self, action, parameter):
        """Open the Keyboard Shortcuts dialog."""
        active_window = self.get_active_window()
        if active_window:
            self.shortcuts_window.set_transient_for(active_window)
            self.shortcuts_window.present()

    def on_about_action(self, *args):
        """Open the About dialog."""
        about = Adw.AboutDialog(application_name='texty2',
                                application_icon='ca.footeware.py.texty2',
                                developer_name='Another fine mess by Footeware.ca',
                                version='1.0.1',
                                developers=['Craig Foote http://Footeware.ca'],
                                copyright='© 2024 Craig Foote')
        about.present(self.get_active_window())

def main(version):
    """The application's entry point."""
    app = Texty2Application()
    return app.run(sys.argv)
