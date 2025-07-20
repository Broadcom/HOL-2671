#!/usr/bin/python3
# version 1.1 - 03 February 2023
# creates ModuleSwitcher desktop launcher shortcut

import os
from pathlib import Path


desktop = '/home/holuser/Desktop'
ms_shortcut = 'modswitcher.desktop'

msdesktop = """
[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Exec=/hol/hol-2671/hol_modswitcher/uistart.sh
Name=Launch Module Switcher
Comment=Module Switcher
Categories=Application;
Icon= /hol/hol-2671/hol_modswitcher/hol-logo.png
Name[en_US.UTF-8]=Module Switcher
    """
with open(f'{desktop}/{ms_shortcut}', "w") as f:
    f.write(msdesktop)
f.close()

os.system(f'chmod 774 {desktop}/{ms_shortcut}')
os.system(f'/usr/bin/gio set {desktop}/{ms_shortcut} metadata::trusted true')
Path(f'{desktop}/{ms_shortcut}').touch()


