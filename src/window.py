# window.py
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

from gi.repository import Adw
from gi.repository import Gtk, Gdk, Gio, GLib

@Gtk.Template(resource_path='/ca/footeware/py/texty2/window.ui')
class Texty2Window(Adw.ApplicationWindow):
    __gtype_name__ = 'Texty2Window'

    save_button = Gtk.Template.Child()
    text_view = Gtk.Template.Child()
    window_title = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    menu_button = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()
        self.settings = Gio.Settings.new('ca.footeware.py.texty2')

        # init window size based on prefs
        width = self.settings.get_int("window-width")
        height = self.settings.get_int("window-height")
        self.set_default_size(width, height)
        self.connect("close-request", self.on_close_request)

        # Font Size action with initial state
        set_font_size_action = Gio.SimpleAction.new_stateful(
           'set_font_size',
           GLib.VariantType.new('i'),
           self.settings.get_value('font-size')
        )
        set_font_size_action.connect("change-state", self.on_set_font_size_action)
        self.add_action(set_font_size_action)
        # init font size based on prefs
        set_font_size_action.activate(self.settings.get_value('font-size'))

        # Toggle Wrap action with initial state
        toggle_wrap_action = Gio.SimpleAction.new_stateful(
           'toggle_wrap',
           None,
           GLib.Variant.new_boolean(self.settings.get_boolean('wrap-mode'))
        )
        toggle_wrap_action.connect("activate", self.on_toggle_wrap_action)
        self.get_application().set_accels_for_action("win.toggle_wrap", ["<primary><shift>W"])
        self.add_action(toggle_wrap_action)
        # init wrap mode based on prefs
        wrap_mode = self.settings.get_boolean("wrap-mode")
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD if wrap_mode else Gtk.WrapMode.NONE)

    def on_toggle_wrap_action(self, action, parameter):
        """Handle Toggle Wrap menu item being clicked."""
        current_state = action.get_state()
        if current_state is not None:
            new_state = not current_state.get_boolean()
        else:
            # Fallback to settings if action state is None
            new_state = not self.settings.get_boolean("wrap-mode")
        action.set_state(GLib.Variant.new_boolean(new_state))
        if new_state:
            self.text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        else:
            self.text_view.set_wrap_mode(Gtk.WrapMode.NONE)
        # Save the wrap mode to prefs
        self.settings.set_boolean("wrap-mode", new_state)

    def on_close_request(self, window):
        """Handle window closing."""
        width = self.get_width()
        height = self.get_height()
        # save window size to prefs
        self.settings.set_int("window-width", width)
        self.settings.set_int("window-height", height)
        return False  # Return False to allow the window to close

    def on_set_font_size_action(self, action, parameter):
        """Handle a Font Size menu item being clicked."""
        action.set_state(parameter)
        size = parameter.get_int32()
        # save font-size as pref
        self.settings.set_int('font-size', size)
        # set font-size using css
        css_provider = Gtk.CssProvider()
        css = f'textview {{ font-size: {size}px; font-family: monospace; }}'.encode('utf-8')
        css_provider.load_from_data(css)
        # Apply CSS to this window's TextView only
        self.text_view.get_style_context().add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

