# Version 1.2.5 - 11-July 2023
#
# Updated Odyssey Game Prep Script for Ubuntu Linux to create desktop shortcut file and Odyssey Launcher script
# Only dolabupdate.py and the icon-256.png are needed in the coreteamonly folder of the bundle
# The Odyssey Client will install in any cloud as long as the vApp is deployed by VLP.
#
# 13-August-2022 removed the lsf.init() call. It is not needed unless interacting with the router.
# 24-June 2023 disable Odyssey for Lab Preview Week - getting Odyssey FAIL
# 24-June 2023 corrected ping loop wait in lsfunctions.py
# 11-July backed out above changes with HOL-2437-v0.15

import sys
import lsfunctions as lsf
import os
import shutil
import datetime
import logging
from pathlib import Path

# default logging level is WARNING (other levels are DEBUG, INFO, ERROR and CRITICAL)
logging.basicConfig(level=logging.DEBUG)

if len(sys.argv) > 1:
    lsf.statusnic = sys.argv[1]
else:
    lsf.statusnic = 'eth5'

if len(sys.argv) > 3:
    lsf.max_minutes_before_fail = int(sys.argv[2])
    lsf.start_time = datetime.datetime.now() - datetime.timedelta(seconds=int(sys.argv[3]))
    lsf.lab_sku = sys.argv[4]

lupdlog = '/hol/labupdater.log'

#
#
# Odyssey Variables
#

updatesource = '/hol/LABUPDATER'
desktop = '/home/holuser/Desktop'
odyssey_dst = '/home/holuser/'
odyssey_app = 'odyssey-client-linux.AppImage'
odyssey_launcher = 'odyssey-launch.sh'
ody_shortcut = 'launch_odyssey.desktop'
ody_icon = 'icon-256.png'

lsf.write_output('===== Beginning LabUpdate process =====', logfile=lupdlog)
lsf.write_output(f'LabStartupFunctions are now available. statusnic:{lsf.statusnic}', logfile=lupdlog)

if os.path.isfile(f'{desktop}/{ody_shortcut}'):
    lsf.write_output('Removing existing Odyssey desktop shortcut.', logfile=lupdlog)
    os.remove(f'{desktop}/{ody_shortcut}')

if os.path.isfile(f'{odyssey_dst}/{ody_icon}'):
    lsf.write_output('Removing existing Odyssey icon.', logfile=lupdlog)
    os.remove(f'{odyssey_dst}/{ody_icon}')

if os.path.isfile(f'{odyssey_dst}/{odyssey_launcher}'):
    lsf.write_output('Removing existing Odyssey launcher.', logfile=lupdlog)
    os.remove(f'{odyssey_dst}/{odyssey_launcher}')

if os.path.isfile(f'{odyssey_dst}/{odyssey_app}'):
    lsf.write_output('Removing existing Odyssey application.', logfile=lupdlog)
    os.remove(f'{odyssey_dst}/{odyssey_app}')

the_cloud = lsf.get_cloudinfo()
if the_cloud == 'NOT REPORTED':
    run_odyssey_prep = False
    lsf.write_output('LabUpdate process not running Odyssey Prep.', logfile=lupdlog)
else:
    lsf.write_output(the_cloud, logfile=lupdlog)
    run_odyssey_prep = False
    odyssey_type = 'V2'

# getting Odyssey fail duing Lab Preview Week
run_odyssey_prep = False
# only run if the pod is deployed by VLP and in an identified cloud org
if run_odyssey_prep:
    statusfile = '/hol/startup_status.txt'
    status = ['not yet']
    while 'Ready' not in status[0]:
        f = open(statusfile, 'r')
        status = f.readlines()
        f.close()
        if 'NOT READY' in status[0].upper():
            status = ['not yet']
        if 'READY' in status[0].upper():
            break
        else:
            lsf.write_output('Waiting for ready...', logfile=lupdlog)
            lsf.labstartup_sleep(lsf.sleep_seconds)

    lsf.write_output('LabUpdate process continuing with Odyssey Prep...', logfile=lupdlog)
    lsf.write_vpodprogress('Odyssey Prep', 'GOOD-8')
    lsf.write_vpodprogress('Install Odyssey', 'GOOD-8')

    # create odyssey_launcher script
    odylaunch = """
    #!/bin/bash
# version 1.0 20 August 2021

ODYSSEY_ROOT=https://odyssey.vmware.com/client/
ODYSSEY_CLIENT=odyssey-client-linux.AppImage

cd ~/Downloads/

echo "********************************************************************************"
echo "*                                                                              *"
echo "* Downloading the latest Odyssey Client...                                     *"
echo "*                                                                              *"
echo ""
curl --proxy "http://192.168.110.1:3128" --progress-bar --remote-name --location "$ODYSSEY_ROOT$ODYSSEY_CLIENT"
echo ""
echo "* Launching the Odyssey Client...                                              *"
echo "*                                                                              *"
echo "********************************************************************************"

win=`xdotool search --name "Odyssey DO NOT EXIT"`
xdotool windowminimize ${win}
chmod 774 $ODYSSEY_CLIENT

#./$ODYSSEY_CLIENT > /dev/null 2>&1 &
echo "#!/usr/bin/bash
nohup /home/holuser/Downloads/odyssey-client-linux.AppImage > /dev/null 2>&1 &
exit" > /tmp/runit.sh
chmod 775 /tmp/runit.sh
nohup /tmp/runit.sh
exit
    """
    with open(f'{odyssey_dst}/{odyssey_launcher}', "w") as f:
        f.write(odylaunch)
        f.close()
    if os.path.isfile(f'{odyssey_dst}/{odyssey_launcher}'):
        lsf.write_output('Installing Odyssey launcher.', logfile=lupdlog)
        os.system(f'chmod 774 {odyssey_dst}/{odyssey_launcher}')

    # move updatesource/ody_icon to odyssey_dst
    if os.path.isfile(f'{updatesource}/{ody_icon}'):
        lsf.write_output('Installing Odyssey icon.', logfile=lupdlog)
        shutil.move(f'{updatesource}/{ody_icon}', f'{odyssey_dst}/{ody_icon}')

    # create the ody_shortcut file
    result = 1
    odydesktop = """
[Desktop Entry]
Version=1.0
Type=Application
Terminal=false
Exec= /usr/bin/gnome-terminal --title=\"Odyssey DO NOT EXIT\" -- /home/holuser/odyssey-launch.sh
Name=Launch Odyssey
Comment=Odyssey Game
Categories=Application;
Icon= /home/holuser/icon-256.png
    """
    with open(f'{desktop}/{ody_shortcut}', "w") as f:
        f.write(odydesktop)
        f.close()

    if os.path.isfile(f'{desktop}/{ody_shortcut}'):
        lsf.write_output('Installing Odyssey desktop shortcut.', logfile=lupdlog)
        os.system(f'chmod 774 {desktop}/{ody_shortcut}')
        result = os.system(f'/usr/bin/gio set {desktop}/{ody_shortcut} metadata::trusted true')
        Path(f'{desktop}/{ody_shortcut}').touch()

    if os.path.isfile(f'{odyssey_dst}/{odyssey_launcher}') and result == 0:
        os.system(f'chmod 774 {odyssey_dst}/{odyssey_launcher}')
        lsf.write_output('*** ODYSSEY LAUNCHER SCRIPT PRESENT ***', logfile=lupdlog)
        lsf.write_vpodprogress('READY', 'ODYSSEY-READY')
    else:
        lsf.write_output('!!! ODYSSEY LAUNCHER ERROR !!!', logfile=lupdlog)
        lsf.write_vpodprogress('ODYSSEY FAIL', 'ODYSSEY-FAIL')

    lsf.write_output(f'Hosting cloud is {the_cloud} ... created Odyssey launcher.', logfile=lupdlog)
else:
    lsf.write_output(f'Hosting cloud is {the_cloud} ... did not run Odyssey prep, but thought about it.', logfile=lupdlog)

lsf.write_output("===== LabUpdate process finished. =====", logfile=lupdlog)

