# labstartup.py - version 1.4 - 23 June 2022

import datetime
import os
import lsfunctions as lsf
from pyVim import connect
import logging

# default logging level is WARNING (other levels are DEBUG, INFO, ERROR and CRITICAL)
logging.basicConfig(level=logging.DEBUG)

# Run the module's Init function (sets global $startTime value to NOW)
lsf.init()
lsf.write_output(f'statusnic is {lsf.statusnic}')

## ATTENTION: Remove the next three lines when you implement this script for your pod
#lsf.write_output('LabStartup script has not been implemented yet. Please ask for assistance if you need it.')
#lsf.write_vpodprogress('Implement LabStartup', 'FAIL-1')
#exit(1)
#
##############################################################################
#  User Variables
##############################################################################
# You must update this variable to the co-op ID of your lab.
# For example, "HOL-1910"
# This data is used for status reporting
vpod_sku = 'HOL-2337'

###
# Use the configured Lab SKU to configure eth5 on vpodrouter
# A bad SKU is a hard failure
if not lsf.labcheck:
    lsf.parse_labsku(vpod_sku)

# standard HOL console resolution
# please use browser zoom if application is not displaying correctly
hol_resolution = '1280x800'

##############################################################################
#  Preliminary Tasks
##############################################################################

###
# because it is easy to adjust the pfSense firewall and accidentally leave it open
# test an external url to be certain the connection is blocked. The last argument is the timeout.
## 
## Nick notes, comment this out, it's all mad about an open firewall that i don't think is open
## and the time reporting is off, seconds != minutes
##
#if not lsf.labcheck:
#    lsf.test_firewall('https://vmware.com', '<title>', 2)

###
# Record whether this is a first run or a LabCheck execution
lsf.test_labcheck()
# NOTE: the script will bail out here if this is a labcheck run and input is detected

# Perform some cleanup. Uses the LabCheck variable to ensure these happen at pod startup only
# if not lsf.labcheck:
#     lsf.cleanfirefoxannoyfile()

if not lsf.labcheck:
    # sometimes the LMC comes up in 1024x600 so just set the standard resolution
    lsf.write_output(f'Setting console resolution to HOL standard {hol_resolution}...')
    result = lsf.run_command(f'/bin/xrandr --display :0 -s {hol_resolution}')


##############################################################################
#  Main LabStartup
##############################################################################

# Please leave these lines here to enable scale testing automation
if lsf.labcheck:
    print('LabCheck is active. Skipping start_autolab.')
else:
    if lsf.start_autolab():
        exit(0)
    else:
        lsf.write_output('No ' + lsf.autolab + ' found, continuing...')

# Report Initial State (recorded on desktop and in /hol/startup_status.txt
if lsf.labcheck:
    lsf.write_output("LabCheck is active.")
    lsf.write_vpodprogress('Not Ready', 'LABCHECK')
else:
    lsf.write_output('Beginning Main script')
    lsf.write_vpodprogress('Not Ready', 'STARTING')

# Does the vPod have external access?
if os.path.exists('/tmp/lupdwired'):
    # wait for the /tmp/lupd file (labupdater.py retrieved the bundle files)
    while not os.path.exists('/tmp/lupd'):
        lsf.write_output("Waiting for labupdater to retrieve bundle...")
        lsf.labstartup_sleep(lsf.sleep_seconds)

# add custom preliminary tasks to /hol/Startup/prelim.py
lsf.startup('prelim.py')

# report initial status for monitoring
lsf.write_vlp_info()
lsf.sendlabhealth()

##############################################################################
# Lab Startup - STEP #1 (vSphere Infrastructure)
##############################################################################

###
# verify vCenter and ESXi hosts are ready then start nested VMs.
# Edit the /hol/Startup/vSphere.py script or include updates in the lab bundle.
lsf.startup('vSphere.py')

# report status after vSphere infrastructure for monitoring
lsf.sendlabhealth()

##############################################################################
#  Intermission - Git pull the latest code from hol-2x37 repo
##############################################################################
import subprocess
import sys
try:
    process = subprocess.run(["/usr/bin/git", "pull"], cwd='/hol/hol-2x37', check=True, capture_output=True, text=True)
    lsf.write_output(process)
    lsf.write_output(process.stdout)
except Exception as e:
    lsf.write_output(e)
    try:
        lsf.write_output(e.stderr)
    except:
        pass
    lsf.write_output("git pull failed, but continuing")
try:
    process = subprocess.run(["/usr/bin/git", "checkout", "2337"], cwd='/hol/hol-2x37', check=True, capture_output=True, text=True)
    lsf.write_output(process)
    lsf.write_output(process.stdout)
except Exception as e:
    lsf.write_output(e)
    try:
        lsf.write_output(e.stderr)
    except:
        pass
    lsf.write_output("git branch checkout failed, but continuing")

##############
# run a wrapper registration script
##############


if not lsf.labcheck:
    try:
        sys.path.append('/hol/hol-2x37/2x37_podsetup')
        import register_wrapper
        register_wrapper.main()
    except Exception as e:
        lsf.write_output(e)
        lsf.write_output("could not import or an error occured with registration script")
        now = datetime.datetime.now()
        delta = now - lsf.start_time
        lsf.labfail('Registration script failed')

else:
    lsf.write_output("labchecking, so we'll skip controller registration")

##############################################################################
# Lab Startup - STEP #3 (Testing Pings)
##############################################################################


###
# Wait here for all hosts in the pings list to respond before continuing
lsf.startup('pings.py')

##############################################################################
# Lab Startup - STEP #4 (Start/Restart/Stop/Query Services and test ports)
##############################################################################

lsf.startup('services.py')

###
# run shell commands on Linux machines
# the format of the file includes the Linux command to use
# ssh key-based authentication is assumed
entries = lsf.read_file_into_list('sshCommands')
if entries:
    lsf.write_vpodprogress('Run ssh Comands', 'GOOD-5')
    for entry in entries:
        (host, cmd) = entry.split('~')
        result = lsf.run_ssh_command(host, cmd)
        lsf.write_output(result)
    lsf.write_output('Finished ssh Commands')

##############################################################################
#  Lab Startup - STEP #5 (Testing URLs)
##############################################################################

###
# Testing URLs
lsf.startup('urls.py')

##############################################################################
#  Lab Startup - STEP #6 (Final validation steps)
##############################################################################

lsf.write_vpodprogress('Running Final Checks', 'GOOD-9')
lsf.write_output('Running Final Checks')


##############################################################################
#  Lab Startup - STEP #6a (Nicks tweak script)
##############################################################################
if not lsf.labcheck:
    try:
        sys.path.append('/hol/hol-2x37/2x37_podsetup')
        import adjustomatic
        adjustomatic.main()
    except Exception as e:
        lsf.write_output(e)
        lsf.write_output("could not import or an error occured with adjustomatic script")
        now = datetime.datetime.now()
        delta = now - lsf.start_time
        lsf.labfail('Adjustomatic script failed')


###
# Add final checks here that are required for your vPod to be marked READY
# Maybe you need to check something after the services are started/restarted.
###

lsf.startup('final.py')

# wait to go ready until getrules.sh is finished on the router
if lsf.statusnic == 'vmx3':
    while True:
        if lsf.router_finished():
            break
        else:
            lsf.report_vpodstatus('READY')
            lsf.write_output("Waiting on router to finish initialization...")
            lsf.labstartup_sleep(lsf.sleep_seconds)

lsf.write_output('Finished Final Checks')
lsf.write_vpodprogress('Finished Final Checks', 'GOOD-9')

###
# create the cron job to run LabStartup check at the interval indicated and record initial ready time
labcheck = False
if not labcheck:
    lsf.write_output(
        'Creating a scheduled task to run LabStartup every ' + str(lsf.labcheckinterval) + ' hour...')
    lsf.create_labcheck_task()

###
# Report current cloud using vPodRouter guestinfo provided by VLP
lsf.write_output('Hosting Cloud: ' + lsf.get_cloudinfo())

###
# Report final Ready state and duration of run
# NOTE: setting READY automatically marks the DesktopInfo badge GREEN
lsf.write_vpodprogress('Ready', 'READY')


delta = datetime.datetime.now() - lsf.start_time
run_mins = "{0:.2f}".format(delta.seconds / 60)
lsf.write_output('LabStartup Finished - runtime was ' + str(run_mins) + ' minutes')
# Since vPodRouter might be rebooted, record initial ready time for LabCheck
# $readyTime = [Math]::Round((Get - RuntimeSeconds $startTime) / 60)
# Set - Content - Value($readyTime) -Path $readyTimeFile
if not lsf.labcheck:
    tempfile = open(lsf.ready_time_file, "w+")
    ready_mins = round(float(run_mins))
    tempfile.write(str(ready_mins) + '\n')
    tempfile.close()

##############################################################################
# Please leave this code here to enable vPod automated checking in HOL-DEV
if lsf.start_autocheck():
    lsf.write_output('Autocheck.ps1 complete.')

##############################################################################

# report final status for monitoring
lsf.sendlabhealth()

# cold lab check
if 'NOT REPORTED' not in lsf.vlp_urn:  # VLP deployment
    lsf.write_output('Cold lab detected. Running labactive.sh...')
    lsf.run_command('/home/holuser/desktop-hol/labactive.sh')