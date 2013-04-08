* Added search and replace functionality to plugin editor (access with
  ``Ctrl`` + ``F`` and ``Ctrl`` + ``H``).
* Added startup script. Can be modified using File->Edit startup script.
* Added context menu for navigation. Includes entries for removing objects
  and an annotation editor.
* Plugin configurations are now restored when saving or refreshing plugins
  and when restarting the program. All plugin configurations can be reset
  to their defaults using Plugins->Restore Plugin configurations.
* A modified plugin is automatically saved before it is run.
* Plugin folders return to their previous state (expanded or minimized)
  when restarting the program.
* Plugin editor tabs can be reordered by dragging.
* Code completion in console can be selected using Enter (in addition to
  Tab as before).

Version 0.2.1
-------------
* New features for plugin editor: Calltips, autocompletion and "jump to"
  (definitions in code or errors displayed in integrated console).
* Experimental support for IPython console (File->New IPython console). Needs
  IPython >= 0.12
* New spectrogram plugin
* Combined filters for filtering (or sorting) a whole list of objects
* "Save all data..." menu option
* Plugins are sorted alphabetically
* New option in plugin menu: Open containing folder
* "Delete" key deletes filters
* Renamed start script from "spyke-viewer" to "spykeviewer"

Version 0.2.0
-------------
Initial documented public release.
