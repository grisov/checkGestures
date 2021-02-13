# NVDA Check Input Gestures

* Author: Oleksandr Gryshchenko
* Version: 1.0
* Download [stable version][1]
* Download [development version][2]
* NVDA compatibility: 2019.3 and beyond

Find and fix input gestures conflicts in NVDA and add-ons. The general term "input gestures" includes keyboard commands, commands entered from Braille keyboards and gestures of touch screens.  
Each of the installed add-ons can make changes to the NVDA configuration by adding or reassigning existing input gestures. If the same input gestures are binded to several functions, it will be impossible to call some of them.  

## Search for duplicate gestures
To detect duplicate gestures, call the NVDA menu, go to the "Tools" submenu, then - "Check Input Gestures" and activate the menu item "Search for duplicate gestures...".  
After that, all input gestures used in NVDA will be checked in the following order:  
1. globalCommands;  
2. globalPlugins.  
If the same input gestures will be detected, which are assigned to different functions, their list will be displayed in a separate dialog box.  
After pressing the Enter key on the selected list item, the corresponding NVDA function will be selected and opened in the standard "Input Gestures..." dialog, where you can delete or reassign the associated gesture.  

Note: As you know, features that don't have a text description do not appear in the "Input Gestures..." dialog. Therefore, after activating such an element, the corresponding warning will be displayed.

## Gestures without description
To view the list of gestures binded with functions without a text description, if they are found in your NVDA configuration, you need to call the NVDA menu, go to the submenu "Tools", then - "Gestures without description...".  
Such features do not appear in the standard NVDA "Input Gestures..." dialog, so it is not yet possible to delete or reassign associated gestures.

## Help
One way to view this help page is to call up the NVDA menu, go to the "Tools" submenu, then - "Check Input Gestures", and activate "Help".

## Change log

### Version 1.0
* implemented search for duplicate input gestures;
* implemented search for input gestures binded to functions without a text description.

## Altering NVDA Check Input Gestures
You may clone this repo to make alteration to NVDA Check Input Gestures.

### Third Party dependencies
These can be installed with pip:
- markdown
- scons
- python-gettext

### To package the add-on for distribution:
1. Open a command line, change to the root of this repo
2. Run the **scons** command. The created add-on, if there were no errors, is placed in the current directory.

[1]: https://github.com/grisov/checkGestures/releases/download/latest/checkGestures.nvda-addon
[2]: https://github.com/grisov/checkGestures/releases/download/latest/checkGestures.nvda-addon
