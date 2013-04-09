.. _api:

API
===

The Spyke Viewer API. It includes the global application configuration,
objects to access the main window and application and convenience functions.

.. data:: spykeviewer.api.config

    Global configuration options for Spyke Viewer. Single options can be set
    by string like a dictionary (e.g.
    ``spykeviewer.api.config['ask_plugin_path'] = False``) or directly (e.g.
    ``spykeviewer.api.config.ask_plugin_path = False``).
    They can be set in the :ref:`startup`, from the
    console or even in plugins. However, some configuration options are only
    effective when changed from the startup script.
    The configurations options are:

    ask_plugin_path (:class:`bool`)
        Ask about plugin paths if saving a file outside of the plugin paths.
        Default: ``True``

    save_plugin_before_starting (:class:`bool`)
        Automatically save and reload a modified plugin before starting.
        Default: ``True``

    load_selection_on_start (:class:`bool`)
        Load the selection that was automatically saved when shutting down
        Spyke Viewer automatically on startup. This parameter is
        only effective when set in the startup script. Default: ``True``

    duplicate_channels (:class:`bool`)
        Treat :class:`neo.core.RecordingChannel` objects that are
        referenced in multiple :class:`neo.core.RecordingChannelGroup`
        objects as separate objects for each reference. If ``False``,
        each channel will only be displayed (and returned by
        :class:`spykeutils.plugin.data_provider.DataProvider`) once,
        for the first reference encountered. Default: ``False``

    codecomplete_console_enter (:class:`bool`)
        Use Enter key for code completion in console. This parameter is
        only effective when set in the startup script. Default: ``True``

    codecomplete_editor_enter (:class:`bool`)
        Use Enter key for code completion in editor. This parameter is
        only effective when set in the startup script. Default: ``True``

    remote_script_parameters (:class:`list`)
        Additional parameters for remote script. Use this if you have a custom
        remote script that needs nonstandard parameters. The format is the same
        as for :class:`subprocess.Popen`, e.g.
        ``['--param1', 'first value', '-p2', '2']``. Default: ``[]``


.. data:: spykeviewer.api.window

    The main window of Spyke Viewer.


.. data:: spykeviewer.api.app

    The PyQt application object.


.. autofunction:: spykeviewer.api.start_plugin

.. autofunction:: spykeviewer.api.get_plugin