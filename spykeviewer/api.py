class __ConfigOptions:
    def __init__(self):
        # Ask about plugin paths if saving a file to a path that is not
        # a plugin path
        self.ask_plugin_path = True
        # Save and reload a modified plugin before starting
        self.save_plugin_before_starting = True
        # Load selection on start
        self.load_selection_on_start = True
        # Default load mode (0 - Regular, 1 - Lazy, 2 - Cached lazy)
        self.load_mode = 0
        # Default cascading mode (False - Regular, True - Lazy)
        self.lazy_cascading = False
        # Use Enter key for code completion in console
        self.codecomplete_console_enter = True
        # Use Enter key for code completion in editor
        self.codecomplete_editor_enter = True
        # Additional parameters for remote script
        self.remote_script_parameters = []
        # Show duplicate channels (those that belong to multiple
        # channel groups) multiple times in navigation
        self.duplicate_channels = False
        # Select all visible segments in navigation by default
        self.autoselect_segments = False
        # Select all visible channel groups in navigation by default
        self.autoselect_channel_groups = False
        # Select all visible channels in navigation by default
        self.autoselect_channels = True
        # Select all visible units in navigation by default
        self.autoselect_units = False

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __getitem__(self, item):
        return self.__dict__[item]


config = __ConfigOptions()
window = None
app = None


def start_plugin(name, current=None, selections=None):
    """ Start first plugin with given name and return result of start()
    method. Raises a SpykeException if not exactly one plugins with
    this name exist.

    :param str name: The name of the plugin. Should not include the
        directory.
    :param current: A DataProvider to use as current selection. If
        ``None``, the regular current selection from the GUI is used.
    :param list selections: A list of DataProvider objects to use as
        selections. If ``None``, the regular selections from the GUI
        are used.
    """
    return window.start_plugin(name, current, selections)


def start_plugin_remote(name, current=None, selections=None):
    """ Start first plugin with given name using the remote script.
    Raises a SpykeException if not exactly one plugins with
    this name exist.

    :param str name: The name of the plugin. Should not include the
        directory.
    :param current: A DataProvider to use as current selection. If
        ``None``, the regular current selection from the GUI is used.
    :param list selections: A list of DataProvider objects to use as
        selections. If ``None``, the regular selections from the GUI
        are used.
    """
    window.start_plugin_remote(name, current, selections)


def get_plugin(name):
    """ Get plugin with the given name. Raises a SpykeException if
    multiple plugins with this name exist. Returns None if no such
    plugin exists.

    :param str name: The name of the plugin. Should not include the
        directory.
    """
    return window.get_plugin(name)


def annotation_editor(neo_object):
    """ Open a graphical annotation editor for a Neo object.

    :param neo_object: Any Neo object.
    """
    window.edit_annotations(neo_object)


def load_files(file_paths):
    """ Open a list files.

    :param list file_paths: The files to open as strings with the full
        file path.
    """
    window.load_files(file_paths)