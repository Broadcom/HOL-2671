#!/usr/bin/python3
# version 1.1 - 03 February 2023
# creates ModuleSwitcher desktop launcher shortcut

import os
from pathlib import Path


desktop = '/home/holuser/Desktop'
ms_shortcut = 'bottraffic.desktop'

msdesktop = """
[Desktop Entry]
Version=1.0
Name=Bot Traffic Generator
GenericName=2337-bottraffic
Exec=/hol/hol-2x37/2x37_podsetup/bot_traffic_stuff/bottraffic.sh
Comment=Generate simulated traffic
Encoding=UTF-8
Icon=/hol/hol-2x37/hol_modswitcher/hol-logo.png
Terminal=true
Type=Application
Categories=Application;Utility;
    """
with open(f'{desktop}/{ms_shortcut}', "w") as f:
    f.write(msdesktop)
f.close()

os.system(f'chmod 774 {desktop}/{ms_shortcut}')
os.system(f'/usr/bin/gio set {desktop}/{ms_shortcut} metadata::trusted true')
Path(f'{desktop}/{ms_shortcut}').touch()