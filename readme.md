# NVDA Check Input Gestures

* Author: Oleksandr Gryshchenko
* Version: 1.2
* NVDA compatibility: 2026.1 and beyond
* Installation: through the NVDA Add-on Store ([stable version][1])

Find and fix the conflicts of input gestures in NVDA and add-ons. Input gestures are the keyboard commands, the commands of braille displays and the gestures of touch screens.

Every installed add-on can add its own input gestures or reassign the existing ones. If the same input gesture is bound to several commands, only one of them works, and the others cannot be used with this gesture.

## Search for duplicate gestures
To search for duplicate gestures, open the NVDA menu (NVDA+N), go to "Tools", "Check Input Gestures" and select "Search for duplicate gestures...". If duplicates are found, they are shown in a window as a tree:

* each duplicate is a branch with its keys and the keyboard layout in parentheses, e.g. "NVDA+Shift+L (keyboard, all layouts)";
* under the keys, the categories of the commands that use them;
* under each category, the commands: the description of the command or the name of its function.

All branches are collapsed at first. Use the arrow keys to move through the tree; the Right and Left arrow keys or Enter expand and collapse a branch. Enter on a command opens the NVDA "Input Gestures" dialog with this command and its gesture selected, so you can change or remove the gesture at once.

A gesture for all keyboard layouts and the same gesture for the current layout are a duplicate, because both work in the current layout. Then both layouts are shown at the keys, and the layout of each command is shown at the command. The same gestures for different layouts, e.g. desktop and laptop, are not duplicates, because only one layout is used at a time.

Commands without a description are not shown in the "Input Gestures" dialog, so their gestures cannot be changed there. The name of their module is shown in square brackets instead of the category, and a warning is shown when such a command is selected.

The search covers the gestures that are available where the focus is: the global commands of NVDA, the global plugins of the add-ons and the program in focus. When the search is started from the NVDA menu, this is the program that had the focus before the menu was opened, as in the NVDA "Input Gestures" dialog. The gestures that work only in other programs are checked when one of those programs has the focus.

## Search when NVDA starts
A few seconds after NVDA has started, when the add-ons have been loaded, the add-on searches for duplicate gestures. The window with the duplicates appears only if new duplicates have appeared since the last time, e.g. after an add-on has been installed. If there are no new duplicates, nothing is shown.

* OK - the duplicates in the window are remembered, and the window appears again only when new duplicates appear.
* Cancel or Escape - the duplicates are not remembered, and the same window appears again when NVDA starts next time.

The "Don't show this window on startup" check box at the bottom of the window turns off the search when NVDA starts. The search from the NVDA menu always shows all duplicates, so the search on startup can be turned on again with the same check box. By default the search on startup is on. After the add-on has been installed, all existing duplicates are new, so the window appears when NVDA starts if there are any duplicates.

The remembered duplicates and the check box are saved in the checkGestures.json file in the NVDA configuration folder at once, even if NVDA is set not to save its configuration on exit.

## Gestures without description
To see the gestures bound to commands without a description, open the NVDA menu, go to "Tools", "Check Input Gestures" and select "Gestures without description...". Such commands are not shown in the NVDA "Input Gestures" dialog, so their gestures cannot be changed or removed there.

## Commands
Both searches can also be run with a command. The commands are listed in the NVDA "Input Gestures" dialog, in the "Check Input Gestures" category, where you can assign your own shortcuts to them. They have no default shortcuts.

To open this help page, open the NVDA menu, go to "Tools", "Check Input Gestures" and select "Help".

## Contributions
We are very grateful to everyone who made the effort to develop, translate and maintain this add-on:

* Jani Kinnunen - Finnish translation;
* Wafiqtaher - Arabic translation;
* Angelo Miguel Abrantes - Portuguese translation;
* Cagri Dogan - Turkish translation;
* Cary Rowen - simplified Chinese translation.

## Change log
The history of changes for each version of the add-on is published on the [Releases page][2] of the add-on repository.

## Altering of add-on source code
You may clone this repo to make alterations to NVDA Check Input Gestures.

Requirements:

* [uv](https://docs.astral.sh/uv/) - manages Python and all development tools of the add-on;
* [GNU Gettext tools](https://mlocati.github.io/articles/gettext-iconv-windows.html) (`msgfmt` and `xgettext` in the `PATH`) - compile translations and generate the template of translatable strings.

Run the following commands from the root of the repository:

1. `uv sync` - install the development dependencies;
2. `uv run prek run --all-files` - run all code checks: linting and formatting with ruff, type checking with pyright and other checks;
3. `uv run python -m unittest discover -s tests -v` - run the unit tests;
4. `uv run scons` - build the add-on, the created `.nvda-addon` file is placed in the root of the repository;
5. `uv run scons pot` - generate the `.pot` file with all translatable strings of the add-on (optional).

[1]: https://addonstore.nvaccess.org/?channel=stable&addonId=checkGestures
[2]: https://github.com/grisov/checkGestures/releases
