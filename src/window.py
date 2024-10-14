import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Adw
from gi.repository import Gtk, Gio, GLib

@Gtk.Template(resource_path='/ca/footeware/py/texty2/window.ui')
class Texty2Window(Adw.ApplicationWindow):
    """The main window containing a textview and a headerbar with menus."""
    __gtype_name__ = 'Texty2Window'

    save_button = Gtk.Template.Child()
    text_view = Gtk.Template.Child()
    toast_overlay = Gtk.Template.Child()
    window_title = Gtk.Template.Child()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.init_template()
        self.settings = Gio.Settings.new('ca.footeware.py.texty2')

        self.current_file = None
        self.buffer_modified = False

        self.buffer = self.text_view.get_buffer()
        self.buffer.connect("changed", self.on_buffer_changed)
        self.buffer_modified = False # Flag to track buffer changes

        # init window size based on prefs
        width = self.settings.get_int("window-width")
        height = self.settings.get_int("window-height")
        self.set_default_size(width, height)
        # Connect to window size change signals
        self.connect("notify::default-width", self.on_window_size_change)
        self.connect("notify::default-height", self.on_window_size_change)

        # Save action
        save_action = Gio.SimpleAction.new("save", None)
        save_action.connect("activate", self.on_save_action)
        self.add_action(save_action)
        self.get_application().set_accels_for_action("win.save", ['<primary>s'])

        # New action
        new_action = Gio.SimpleAction.new("new", None)
        new_action.connect("activate", self.on_new_action)
        self.add_action(new_action)
        self.get_application().set_accels_for_action("win.new", ['<primary>n'])

        # Open action
        open_action = Gio.SimpleAction.new("open", None)
        open_action.connect("activate", self.on_open_action)
        self.add_action(open_action)
        self.get_application().set_accels_for_action("win.open", ['<primary>o'])

        # Save As action
        save_as_action = Gio.SimpleAction.new("save-as", None)
        save_as_action.connect("activate", self.on_save_as_action)
        self.add_action(save_as_action)
        self.get_application().set_accels_for_action("win.save-as", ['<primary><shift>s'])

        # Font Size action with initial state
        set_font_size_action = Gio.SimpleAction.new_stateful(
           'set-font-size',
           GLib.VariantType.new('i'),
           self.settings.get_value('font-size')
        )
        set_font_size_action.connect("change-state", self.on_set_font_size_action)
        self.add_action(set_font_size_action)
        # init font size based on prefs
        set_font_size_action.activate(self.settings.get_value('font-size'))

        # Toggle Wrap action with initial state
        toggle_wrap_action = Gio.SimpleAction.new_stateful(
           'toggle-wrap',
           None,
           GLib.Variant.new_boolean(self.settings.get_boolean('wrap-mode'))
        )
        toggle_wrap_action.connect("activate", self.on_toggle_wrap_action)
        self.get_application().set_accels_for_action("win.toggle-wrap", ["<primary><shift>W"])
        self.add_action(toggle_wrap_action)
        # init wrap mode based on prefs
        wrap_mode = self.settings.get_boolean("wrap-mode")
        self.text_view.set_wrap_mode(Gtk.WrapMode.WORD if wrap_mode else Gtk.WrapMode.NONE)

        self.text_view.grab_focus()

    def on_save_action(self, action, parameters=None):
        self.save_file()

    def save_file(self):
        if self.current_file:
            return self.save_to_file(self.current_file)
        else:
            return self.save_as()

    def save_to_file(self, file):
        buffer = self.text_view.get_buffer()
        text = buffer.get_text(buffer.get_start_iter(), buffer.get_end_iter(), True)
        try:
            with open(file.get_path(), 'w') as f:
                f.write(text)
            self.window_title.set_title(f"{file.get_basename()}")
            self.window_title.set_subtitle(file.get_path())
            self.buffer_modified = False
            self.text_view.get_buffer().set_modified(False)
            self.show_toast(f"File saved: {file.get_basename()}")
            return True
        except IOError as e:
            self.show_toast(f"Error saving file: {str(e)}")
            return False

    def save_as(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Save File")
        dialog.save(self, None, self.on_save_dialog_response)

    def on_save_action(self, action, parameters=None):
        self.save_file()

    def on_save_dialog_response(self, dialog, result):
        try:
            file = dialog.save_finish(result)
            if file:
                if self.save_to_file(file):
                    self.current_file = file
                    self.buffer_modified = False
                    self.text_view.get_buffer().set_modified(False)
            else:
                self.show_toast("Save operation cancelled")
        except GLib.Error as error:
            self.show_toast(f"Error saving file: {error.message}")

    def load_file(self, file):
        try:
            with open(file.get_path(), 'r') as f:
                text = f.read()
            buffer = self.text_view.get_buffer()
            buffer.set_text(text)
            self.current_file = file
            self.show_toast(f"File opened: {file.get_basename()}")
        except IOError as e:
            self.show_toast(f"Error opening file: {str(e)}")

    def on_new_action(self, action, parameters=None):
        self.new_file()

    def new_file(self):
        if self.buffer_modified:
            self.prompt_save_changes("new")
        else:
            self.create_new_file()

    def create_new_file(self):
        self.text_view.get_buffer().set_text("")
        self.text_view.get_buffer().set_modified(False)
        self.current_file = None
        self.window_title.set_title("texty2")
        self.window_title.set_subtitle("a minimal text editor")
        self.show_toast("New file created")
        self.buffer_modified = False
        self.text_view.get_buffer().set_modified(False)

    def prompt_save_changes(self, next_action):
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Save changes?")
        dialog.set_body("There are unsaved changes. Do you want to save them?")
        dialog.add_response("cancel", "Cancel")
        dialog.add_response("discard", "Discard")
        dialog.add_response("save", "Save")
        dialog.set_default_response("save")
        dialog.set_close_response("cancel")
        dialog.set_response_appearance("save", Adw.ResponseAppearance.SUGGESTED)
        dialog.set_response_appearance("discard", Adw.ResponseAppearance.DESTRUCTIVE)

        dialog.connect("response", self.on_save_changes_response, next_action)
        dialog.present()

    def on_save_changes_response(self, dialog, response, next_action):
        if response == "save":
            success = self.save_file()
            if success:
                self.execute_next_action(next_action)
        elif response == "discard":
            self.execute_next_action(next_action)
        # If "cancel" or dialog is closed, do nothing

    def execute_next_action(self, next_action):
        if next_action == "new":
            self.create_new_file()
            self.text_view.grab_focus()
        elif next_action == "open":
            self.open_file(self)

    def open_file(self):
        dialog = Gtk.FileDialog.new()
        dialog.set_title("Open File")
        dialog.open(self, None, self.on_open_dialog_response)

    def save_file(self):
        if self.current_file:
            return self.save_to_file(self.current_file)
        else:
            return self.save_as()

    def on_open_action(self, action, parameters=None):
        if self.buffer_modified:
            self.prompt_save_changes("new")
        else:
            dialog = Gtk.FileDialog.new()
            dialog.set_title("Open File")
            dialog.open(self, None, self.on_open_dialog_response)

    def on_open_dialog_response(self, dialog, result):
        try:
            file = dialog.open_finish(result)
            if file:
                self.load_file(file)
                self.window_title.set_title(f"{file.get_basename()}")
                self.window_title.set_subtitle(file.get_path())
                self.buffer_modified = False
                self.buffer.set_modified(False)
            else:
                self.show_toast("Open operation cancelled")
        except GLib.Error as error:
            self.show_toast(f"Error opening file: {error.message}")

    def on_save_as_action(self, action, parameters=None):
        self.save_as()

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

    def on_window_size_change(self, window, parameter):
        """Handle window resizing."""
        width = self.get_width()
        height = self.get_height()
        # save window size to prefs
        self.settings.set_int("window-width", width)
        self.settings.set_int("window-height", height)

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

    def show_toast(self, message):
        toast = Adw.Toast.new(message)
        self.toast_overlay.add_toast(toast)

    def on_buffer_changed(self, buffer):
        self.buffer_modified = True
        title_str = self.window_title.get_title()
        if not title_str.startswith("* "):
            self.window_title.set_title(f"* {title_str}")
