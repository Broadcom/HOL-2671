# Version 1.0 - 20-August-2021
#
# NEW Odyssey Game Prep Script for Ubuntu Linux
#

import sys
sys.path.append('/hol')
import lsfunctions as lsf
import os
import shutil
from pathlib import Path
import subprocess
import time


def verify_proxy():
    """
    This function loops through all of the Ubuntu proxy environment variables and sets correctly if needed
    since the odyssey_launch.sh script uses curl with an explicit proxy command line option
    this function is not needed but will leave as an example and if needed for other purposes
    """
    proxies = ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY']
    tp = 'http://192.168.110.1:3128'
    tps = 'https://192.168.110.1:3128'
    for proxy in proxies:
        ctp = ''
        # noinspection PyUnusedLocal,PyBroadException
        try:
            envproxy = os.getenv(proxy)
            if tp not in envproxy:
                if 's' in proxy or 'S' in proxy:
                    ctp = tps
                else:
                    ctp = tp
        except Exception as e:
            if 's' in proxy or 'S' in proxy:
                ctp = tps
            else:
                ctp = tp
        lsf.write_output(f'Setting {proxy} to {ctp}')
        os.environ[proxy] = ctp


# IMPORTANT: change this to the co-op ID of your pod!
vpodsku = 'HOL-2237'

# IMPORTANT: Must run the lsf.init() function to get the routerpwprompt
lsf.init()

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

# in which cloud(s) will Odyssey prep using the v2 client occur? (concat org names in ALL lowercase)
odyssey_v2_cloud_orgs = 'sc1-vcd04-hol-u'
odyssey_v2_cloud_orgs += 'sc1-vcd02-vmworld-u'
odyssey_v2_cloud_orgs += 'sc1-vcd02-hol-u'
odyssey_v2_cloud_orgs += 'wdc-vcd03-vmworld-u'
odyssey_v2_cloud_orgs += 'wdc-vcd03-hol-u'
odyssey_v2_cloud_orgs += 'us04-3-hol-dev-d'  # for Self-serve Functional Testing

lsf.write_output('===== Beginning LabUpdate process =====')
lsf.write_output('LabStartupFunctions are now available.')
lsf.parse_labsku(vpodsku)

if os.path.isfile(f'{desktop}/{ody_shortcut}'):
    lsf.write_output('Removing existing Odyssey desktop shortcut.')
    os.remove(f'{desktop}/{ody_shortcut}')

if os.path.isfile(f'{odyssey_dst}/{ody_icon}'):
    lsf.write_output('Removing existing Odyssey icon.')
    os.remove(f'{odyssey_dst}/{ody_icon}')

if os.path.isfile(f'{odyssey_dst}/{odyssey_launcher}'):
    lsf.write_output('Removing existing Odyssey launcher.')
    os.remove(f'{odyssey_dst}/{odyssey_launcher}')

if os.path.isfile(f'{odyssey_dst}/{odyssey_app}'):
    lsf.write_output('Removing existing Odyssey application.')
    os.remove(f'{odyssey_dst}/{odyssey_app}')

the_cloud = lsf.get_cloudinfo()
#the_cloud = 'us04-3-hol-dev-d'  # DEBUG only. comment out
run_odyssey_prep = False
if the_cloud in odyssey_v2_cloud_orgs:
    lsf.write_output(the_cloud)
    run_odyssey_prep = True
    odyssey_type = 'V2'
else:
    lsf.write_output('LabUpdate process not running Odyssey Prep.')

#fix kubelet cert

while True:
    try:
        stdout=subprocess.run(["/home/holuser/.local/bin/ansible-playbook", "/hol/hol-2x37/2x37_podsetup/kubefixer.yml", "-i", "/hol/hol-2x37/2x37_podsetup/inventory.yml"], capture_output=True, text=True)
        if stdout.returncode != 0:
            raise Exception(stdout)
        print(stdout)
        break
    except Exception as e:
        print(e)
        print("waiting 30 seconds for retry")
        time.sleep(30)



# only run if the pod is deployed by VLP and in an identified cloud org
if run_odyssey_prep:
    statusfile = '/hol/startup_status.txt'
    status = ['not yet']
    while 'Ready' not in status[0]:
        lsf.write_output('Waiting for ready...')
        f = open(statusfile, 'r')
        status = f.readlines()
        if 'Not Ready' in status[0]:
            status = ['not yet']
        lsf.labstartup_sleep(lsf.sleep_seconds)

    lsf.write_output('LabUpdate process continuing with Odyssey Prep...')
    lsf.write_vpodprogress('Odyssey Prep', 'GOOD-8')
    lsf.write_vpodprogress('Install Odyssey', 'GOOD-8')
    # move updateSource/odyssey_launcher to odyssey_dst
    if os.path.isfile(f'{updatesource}/{odyssey_launcher}'):
        lsf.write_output('Installing Odyssey launcher.')
        os.system(f'chmod 774 {updatesource}/{odyssey_launcher}')
        shutil.move(f'{updatesource}/{odyssey_launcher}', f'{odyssey_dst}/{odyssey_launcher}')
    # move updatesource/ody_icon to odyssey_dst
    if os.path.isfile(f'{updatesource}/{ody_icon}'):
        lsf.write_output('Installing Odyssey icon.')
        shutil.move(f'{updatesource}/{ody_icon}', f'{odyssey_dst}/{ody_icon}')

    # move updateSource/ody_shortcut to desktop
    result = 1
    if os.path.isfile(f'{updatesource}/{ody_shortcut}'):
        lsf.write_output('Installing Odyssey desktop shortcut.')
        os.system(f'chmod 774 {updatesource}/{ody_shortcut}')
        shutil.move(f'{updatesource}/{ody_shortcut}', f'{desktop}/{ody_shortcut}')
        result = os.system(f'/usr/bin/gio set {desktop}/{ody_shortcut} metadata::trusted true')
        Path(f'{desktop}/{ody_shortcut}').touch()

    if os.path.isfile(f'{odyssey_dst}/{odyssey_launcher}') and result == 0:
        lsf.write_output('*** ODYSSEY LAUNCHER DOWNLOADED ***')
        lsf.write_vpodprogress('READY', 'ODYSSEY-READY')
    else:
        lsf.write_output('!!! ODYSSEY LAUNCHER ERROR !!!')
        lsf.write_vpodprogress('ODYSSEY FAIL', 'ODYSSEY-FAIL')

    lsf.write_output(f'Hosting cloud is {the_cloud} ... retrieved Odyssey launcher.')
else:
    lsf.write_output(f'Hosting cloud is {the_cloud} ... did not run Odyssey prep, but thought about it.')

lsf.write_output("===== LabUpdate process finished. =====")
