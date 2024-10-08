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
from gi.repository import Gtk

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
        self.apply_initial_font_size()

    def apply_initial_font_size(self):
        app = self.get_application()
        if app:
            saved_size = app.settings.get_int('font-size')
            css_provider = Gtk.CssProvider()
            css = f'textview {{ font-size: {saved_size}px; font-family: monospace; }}'.encode('utf-8')
            css_provider.load_from_data(css)
            self.text_view.get_style_context().add_provider(
                css_provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )

