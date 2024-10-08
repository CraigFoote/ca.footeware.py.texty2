# main.py
#
# Copyright 2024 Craig
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

import sys
import gi

gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Gio, Adw, GLib, Gdk
from .window import Texty2Window


class Texty2Application(Adw.Application):
    """The main application singleton class."""

    def __init__(self):
        super().__init__(application_id='ca.footeware.py.texty2',
                         flags=Gio.ApplicationFlags.DEFAULT_FLAGS)

        self.settings = Gio.Settings.new('ca.footeware.py.texty2')

        self.create_action('quit', lambda *_: self.quit(), ['<primary>q'])
        self.create_action('about', self.on_about_action)
        self.create_action('preferences', self.on_preferences_action)

        # Create the set_font_size action with a state
        set_font_size_action = Gio.SimpleAction.new_stateful(
           'set_font_size',
           GLib.VariantType.new('i'),  # Make sure this is 'i' for integer
           self.settings.get_value('font-size')  # Default font size
        )
        set_font_size_action.connect("activate", self.on_set_font_size_action)
        self.add_action(set_font_size_action)

        action = self.lookup_action('set_font_size')
        if action:
           print("set_font_size action found")
        else:
           print("set_font_size action not found")

    def do_activate(self):
        win = self.props.active_window
        if not win:
            win = Texty2Window(application=self)
        win.present()

        # Apply the saved font size
        saved_size = self.settings.get_int('font-size')
        self.activate_action('set_font_size', GLib.Variant.new_int32(saved_size))

    def on_set_font_size_action(self, action, parameter):
        size = parameter.get_int32()
        action.set_state(parameter)
        self.settings.set_int('font-size', size)
        css_provider = Gtk.CssProvider()
        css = f'textview {{ font-size: {size}px; font-family: monospace; }}'.encode('utf-8')
        css_provider.load_from_data(css)
        win = self.props.active_window
        if win and hasattr(win, 'text_view'):
            win.text_view.get_style_context().add_provider(
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

    def on_about_action(self, *args):
        """Callback for the app.about action."""
        about = Adw.AboutDialog(application_name='texty2',
                                application_icon='ca.footeware.py.texty2',
                                developer_name='Craig',
                                version='0.1.0',
                                developers=['Craig'],
                                copyright='© 2024 Craig')
        # Translators: Replace "translator-credits" with your name/username, and optionally an email or URL.
        about.set_translator_credits(_('translator-credits'))
        about.present(self.props.active_window)

    def on_preferences_action(self, widget, _):
        """Callback for the app.preferences action."""
        print('app.preferences action activated')

    def create_action(self, name, callback, shortcuts=None, param_type=None):
        """Add an application action.

        Args:
            name: the name of the action
            callback: the function to be called when the action is activated
            shortcuts: an optional list of accelerators
            param_type: the parameter type for the action (if any)
        """
        if param_type:
            action = Gio.SimpleAction.new(name, param_type)
        else:
            action = Gio.SimpleAction.new(name, None)
        action.connect("activate", callback)
        self.add_action(action)
        if shortcuts:
            self.set_accels_for_action(f"app.{name}", shortcuts)


def main(version):
    """The application's entry point."""
    app = Texty2Application()
    return app.run(sys.argv)
