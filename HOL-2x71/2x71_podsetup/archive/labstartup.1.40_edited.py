# work in progress
# labstartup.py - version 0.1.40 - 08 June 2021

import datetime
import lsfunctions as lsf
from pyVim import connect

# reduce ESXi MM and DRS tests if not in MM and no vCSL machines 06/08/2021

# Run the module's Init function (sets global $startTime value to NOW)
# Doubt this is needed
lsf.init()

# ATTENTION: Remove the next three lines when you implement this script for your pod
# lsf.write_output('LabStartup script has not been implemented yet. Please ask for assistance if you need it.')
# lsf.write_vpodprogress('Implement LabStartup', 'FAIL-1')
# exit()

##############################################################################
#  User Variables
##############################################################################
# You must update this variable to the co-op ID of your lab.
# For example, "HOL-1910"
# This data is used for status reporting
vpod_sku = 'HOL-2237'

##############################################################################
#  Preliminary Tasks
##############################################################################

###
# Record whether this is a first run or a LabCheck execution
lsf.test_labcheck()
# NOTE: the script will bail out here if this is a labcheck run and input is detected

# Perform some cleanup. Uses the LabCheck variable to ensure these happen at pod startup only
if not lsf.labcheck:
    lsf.cleanfirefoxannoyfile()

###
# Use the configured Lab SKU to configure eth5 on vpodrouter
# A bad SKU is a hard failure
lsf.parse_labsku(vpod_sku)

##############################################################################
#  Main LabStartup
##############################################################################

# Please leave these lines here to enable scale testing automation
if lsf.labcheck:
    print('LabCheck is active. Skipping start_autolab.')
else:
    if lsf.start_autolab():
        exit()
    else:
        lsf.write_output('No ' + lsf.autolab + ' found, continuing...')

# Report Initial State (recorded on desktop and in /hol/startup_status.txt
if lsf.labcheck:
    lsf.write_output("LabCheck is active.")
    lsf.write_vpodprogress('Not Ready', 'LABCHECK')
else:
    lsf.write_output('Beginning Main script')
    lsf.write_vpodprogress('Not Ready', 'STARTING')



##############################################################################
# Lab Startup - STEP #1 (Infrastructure)
##############################################################################

###
# Testing that vESXi hosts are online: all hosts must respond before continuing
esx_hosts = lsf.read_file_into_list('ESXiHosts')
if esx_hosts:
    lsf.write_vpodprogress("Checking vESXi", 'STARTING')
for host in esx_hosts:
    while not lsf.test_tcp_port(host, 22):
        lsf.write_output('Cannot connect to ' + host + ' on port 22')
        lsf.labstartup_sleep(lsf.sleep_seconds)

###
# connect to all vCenters
# this could be an ESXi host
vcenters = lsf.read_file_into_list('vCenters')
if vcenters:
    lsf.write_vpodprogress('Connecting vCenters', 'STARTING')
    lsf.connect_vcenters(vcenters)

###
# check Datastores
if vcenters:
    lsf.write_vpodprogress('Checking Datastores', 'STARTING')
    datastores = lsf.read_file_into_list('Datastores')
    for entry in datastores:
        while not lsf.check_datastore(entry):
            lsf.labstartup_sleep(lsf.sleep_seconds)

###
# ESXi hosts must exit maintenance mode
# if vcenters:
#     if not lsf.check_maintenance():
#         lsf.write_vpodprogress('Exit Maintenance', 'STARTING')
#         lsf.write_output('Taking ESXi hosts out of Maintenance Mode...')
#         lsf.exit_maintenance()
#         lsf.write_output('Pausing 2 minutes to let ESXi hosts stabilize.')
#         lsf.labstartup_sleep(120)  # pausing 2 minutes before exiting MM

###
# verify the vcls VMs have started
# vcls_vms = 0
# if vcenters:
#     vms = lsf.get_all_vms()
#     for vm in vms:
#         if "vCLS" in vm.name:
#             vcls_vms = vcls_vms + 1
#             while not vm.runtime.powerState == "poweredOn":
#                 lsf.write_output(f'Waiting for {vm.name} to power on...')
#                 lsf.labstartup_sleep(lsf.sleep_seconds)
#     if vcls_vms > 0:
#         lsf.write_output('All vCLS VMs have started...')

###
# verify DRS is enabled (remove if DRS is disabled intentionally)
# if vcenters and vcls_vms > 0:
#     clusters = lsf.get_all_clusters()
#     for cluster in clusters:
#         while not cluster.configuration.drsConfig.enabled:
#             lsf.write_output(f'Waiting for DRS to enable on {cluster.name}...')
#     lsf.write_output('DRS is enabled on all clusters.')

# maint = 0
# if vcenters:
#     while not lsf.check_maintenance():
#         maint = maint + 1
#         lsf.write_output('Waiting for ESXi hosts to exit Maintenance Mode...')
#         lsf.labstartup_sleep(lsf.sleep_seconds)
#     if maint > 0:
#         lsf.write_output('All ESXi hosts are out of Maintenance Mode.')


##############################################################################
#  Intermission - Git pull the latest code from hol-2237 repo
##############################################################################
import subprocess
import sys
try:
    process = subprocess.check_output(["/usr/bin/git", "pull"], cwd='/hol/hol-2x37')
    print(process)
except Exception as e:
    print(e)
    print("git pull failed, but continuing")


##############################################################################
#      Lab Startup - STEP #2 (Starting Nested VMs and vApps)
##############################################################################

###
# Use the Start-Nested function to start batches of nested VMs and/or vApps
# Create additional arrays for each batch of VMs and/or vApps
# Insert a LabStartup-Sleep as needed if a pause is desired between batches
# Or include additional tests for services after each batch and before the next batch

if vcenters:
    lsf.write_vpodprogress('Starting vVMs', 'GOOD-2')
    lsf.write_output('Starting vVMs')
    vms = lsf.read_file_into_list('VMs')
    lsf.start_nested(vms)
    lsf.write_output('Starting vApps')
    vapps = lsf.read_file_into_list('vApps')
    lsf.start_nested(vapps)

if vcenters:
    lsf.write_output('Clearing host connection and power state alerts')
    # clear the bogus alarms
if vcenters:
    lsf.clear_host_alarms()

###
# Disconnect from vCenters  (10/22, Nick, moved to end of script to facilitate multiple vvm startups)
# Do not do this here if you need to perform other actions within vCenter
#  in that case, move this block later in the script. Need help? Please ask!

# if vcenters:
#     lsf.write_output('Disconnecting vCenters...')
#     for si in lsf.sis:
#         # print ("disconnect", si) # how do I find the members of ServiceInstance?
#         # inspect.getsource(si)
#         connect.Disconnect(si)

##############################################################################
# Lab Startup - STEP #3 (Testing Pings)
##############################################################################

###
# Wait here for all hosts in the pings list to respond before continuing
pings = lsf.read_file_into_list('Pings')
if pings:
    lsf.write_vpodprogress('Waiting for pings', 'GOOD-3')
    for ping in pings:
        lsf.test_ping(ping)

##############################################################################
# Lab Startup - STEP #4 (Start/Restart/Stop/Query Services and test ports)
##############################################################################

###
# Manage Windows services on remote Windows machines
# options are "start", "restart", "stop" or "query"
entries = lsf.read_file_into_list('WindowsServices')
if entries:
    action = 'start'
    lsf.write_vpodprogress('Manage Windows Services', 'GOOD-4')
    for entry in entries:
        (host, service, p, ws) = entry.split(':')
        if not p:
            p = lsf.password
        if not ws:
            ws = 5
        result = lsf.managewindowsservice(action, host, service, waitsec=int(ws), pw=p)
        lsf.write_output(result)
    lsf.write_output('Finished start Windows services')

###
# run shell commands on Linux machines
# the format of the file includes the Linux command to use
# ssh key-based authentication is assumed
entries = lsf.read_file_into_list('sshCommands')
if entries:
    lsf.write_vpodprogress('Run ssh Comands', 'GOOD-5')
    for entry in entries:
        (host, cmd) = entry.split(':')
        result = lsf.run_ssh_command(host, cmd)
        lsf.write_output(result)
    lsf.write_output('Finished ssh Commands')

# Manage Linux services on remote machines
# options are "start", "restart", "stop" or "query"
entries = lsf.read_file_into_list('LinuxServices')
if entries:
    action = 'start'
    lsf.write_vpodprogress('Manage Linux Services', 'GOOD-5')
    for entry in entries:
        (host, service, p, ws) = entry.split(':')
        if not p:
            p = ''
        if not ws:
            ws = 5
        lsf.write_output(f'Performing {action} {service} on {host}')
        result = lsf.managelinuxservice(action, host, service, waitsec=int(ws), pw=p)
        lsf.write_output(result)
    lsf.write_output(f'Finished {action} Linux Services.')


##############################################################################
#  Lab Startup - retry start VMs before TCP ports get tested
##############################################################################

lsf.write_output('Starting vVMs again')
vms = lsf.read_file_into_list('VMs')
lsf.start_nested(vms)


##############################################################################
#  Lab Startup - continue on with step #4, testing TCP ports now
##############################################################################
###
# Ensure services in the $TCPServices array are answering on specified ports
entries = lsf.read_file_into_list('TCPServices')
if entries:
    lsf.write_vpodprogress('Testing TCP Ports', 'GOOD-6')
    for entry in entries:
        (host, port) = entry.split(':')
        while not lsf.test_tcp_port(host, port):
            lsf.labstartup_sleep(lsf.sleep_seconds)
    lsf.write_output('Finished testing TCP ports')

##############################################################################
#  Lab Startup - STEP #5 (Testing URLs)
##############################################################################

###
# Testing URLs
urls = lsf.read_file_into_list('URLs')
if urls:
    lsf.write_output('Testing URLS')
    lsf.write_vpodprogress('Checking URLs', 'GOOD-7')
    for entry in urls:
        url = entry.split(',')
        #  not_ready: optional pattern if present means not ready verbose: display the html
        #  lsf.test_url(url[0], url[1], not_ready='not yet', verbose=True)
        while not lsf.test_url(url[0], url[1]):
            lsf.labstartup_sleep(lsf.sleep_seconds)

    lsf.write_output('Finished testing URLs')

###
# Disconnect from vCenters  (10/22, Nick, this is the new home)
# Do not do this here if you need to perform other actions within vCenter
#  in that case, move this block later in the script. Need help? Please ask!

if vcenters:
    lsf.write_output('Disconnecting vCenters...')
    for si in lsf.sis:
        # print ("disconnect", si) # how do I find the members of ServiceInstance?
        # inspect.getsource(si)
        connect.Disconnect(si)

##############################################################################
#  Lab Startup - STEP #6 (Final validation steps)
##############################################################################

lsf.write_vpodprogress('Running Final Checks', 'GOOD-9')
lsf.write_output('Running Final Checks')




##############################################################################
#  Lab Startup - STEP #6a (Nicks tweak script)
##############################################################################
try:
    sys.path.append('/hol/hol-2x37/2x37_podsetup')
    import adjustomatic
    adjustomatic.main()
except Exception as e:
    print(e)
    print("could not import or an error occured with adjustomatic script")
    now = datetime.datetime.now()
    delta = now - lsf.start_time
    lsf.labfail('BAD ISSUE', delta.seconds)

###
# Add final checks here that are required for your vPod to be marked READY
# Maybe you need to check something after the services are started/restarted.
###

# example addroute command for testing
# lsf.addroute('10.40.14.0', '255.255.255.0', '192.168.120.5')

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
# $cloudInfo = Get - CloudInfo
cloudinfo = lsf.get_cloudinfo()
lsf.write_output('Hosting Cloud: ' + cloudinfo)

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