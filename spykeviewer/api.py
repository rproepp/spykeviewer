config = {}

# Ask about plugin paths if saving a file to a path that is not
# a plugin path
config['ask_plugin_path'] = True
# Save and reload a modified plugin before starting
config['save_plugin_before_starting'] = True
# Use Enter key for code completion in console
config['codecomplete_console_enter'] = True
# Use Enter key for code completion in editor
config['codecomplete_editor_enter'] = True
# Additional parameters for remote script
config['remote_script_parameters'] = []
# Multiple channels in view
config['duplicate_channels'] = False


window = None
app = None


def start_plugin(name):
    """ Start first plugin with given name and return result of start()
    method. Raises a SpykeException if not exactly one plugins with
    this name exist.

    :param str name: The name of the plugin. Should not include the
        directory.
    """
    return window.start_plugin(name)


def get_plugin(name):
    """ Get plugin with the given name. Raises a SpykeException if
    multiple plugins with this name exist. Returns None if no such
    plugin exists.

    :param str name: The name of the plugin. Should not include the
        directory.
    """
    return window.get_plugin(name)




