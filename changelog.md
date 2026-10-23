## Version 1.2.0

### Added

- The duplicate gestures are shown as a tree: each duplicate is a branch with its keys and keyboard layouts, then the categories of the commands that use them, then the commands. All branches are collapsed at first, so all duplicates can be seen at once.
- Activating a command in the tree opens the NVDA Input Gestures dialog with this command and its gesture selected, so the gesture can be changed or removed at once. If a future version of NVDA changes this dialog, only the search result is shown there, as before.
- A few seconds after NVDA has started, the add-on searches for duplicate gestures and shows them only if new duplicates have appeared since the last time, e.g. after an add-on has been installed. The duplicates are remembered when the window is closed with OK; after Cancel the same window appears again when NVDA starts next time.
- A check box in the window of duplicates turns off the search when NVDA starts. It is saved at once in the add-on's own file, even if NVDA is set not to save its configuration on exit.

### Changed

- When the search is started from the NVDA menu, the gestures of the program that had the focus before the menu are checked, as in the NVDA Input Gestures dialog.
- A gesture for all keyboard layouts and the same gesture for the current layout are shown as one duplicate, with both layouts.
- The duplicates, categories and commands are sorted by name.
- Tested with NVDA 2026.3.

### Fixed

- The window of duplicates had an empty list with the same label above the list of gestures.
