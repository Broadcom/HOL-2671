import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import paramiko
import ssl
from pyVmomi import vim, vmodl

import functions.file_functions as file
import functions.vm_functions as vmf
import functions.fleet_functions as fleet
import functions.core_functions as core

debug = False
sslVerify = False
vSanTimeout = 2700

def updateShutdownList(shutdownList, vmList, hostList):

    if len(vmList) > 0 :
        print(f"INFO: Adding {vmList} Virtual Machines to Shutdown List.")

    try:
        for host in hostList:
            username = hostList[host]['config']['username']
            password = hostList[host]['config']['password']
            
            for vmName in vmList:

                vm = vmf.vmExists(host, username, password, vmName)
                if vm:
                    jTemp = {
                        vm.name : {
                            'config': {
                                'host' : host,
                                'username' : esxUsername,
                                'password' : esxPassword
                            }
                        }
                    }
                    shutdownList.update(jTemp)
    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        return shutdownList
        


## VARIABLES

pwdFile = '/home/holuser/Desktop/PASSWORD.txt'

mgmtVcFqdn = 'vc-mgmt-a.site-a.vcf.lab'
mgmtVcUsername = 'administrator@vsphere.local'
mgmtVcPassword = file.readFile(pwdFile)

wldVcFqdn = 'vc-wld01-a.site-a.vcf.lab'
wldVcUsername = 'administrator@wld.sso'
wldVcPassword = file.readFile(pwdFile)

esxUsername = 'root'
esxPassword = file.readFile(pwdFile)

lcmFqdn = 'opslcm-a.site-a.vcf.lab'
lcmUsername = 'admin@local'
lcmPassword = file.readFile(pwdFile)

patterns = [
    "^([{]?dev-project-{1}[}]?)([{]?[0-9a-zA-Z]{5}-[0-9a-zA-Z]{5}[}]?$)",
    "^([{]?dev-project-worker-{1}[}]?)([{]?[0-9a-zA-Z]{5}-[0-9a-zA-Z]{8,}-[0-9a-zA-Z]{5}[}]?$)",
    "^([{]?cci-service-{1}[}]?)([{]?[0-9a-z]{10}-[0-9a-z]{5}[}]?$)",
    "^([{]?cci-service-{1}[}]?)([{]?[0-9a-z]{10}-[0-9a-z]{5}[}]?$)",
    "^([{]?vCLS-{1}[}]?)([{]?[0-9a-fA-F]{8}-([0-9a-fA-F]{4}-){3}[0-9a-fA-F]{12}[}]?$)"
]

sepatterns = ["^wld_a_Avi-se-[a-z]{5}$"]

vcfMgmtList = ['auto-a-8fpl5','ops-a','opscollector-01a','opslcm-a', 'alb-a-node0']
vcfList = ['sddcmanager-a','vc-wld01-a','vc-mgmt-a']
vksList = ['SupervisorControlPlaneVM (1)']
vcfNsxList = ['edge-wld01-01a','edge-wld01-02a','nsx-mgmt-01a', 'nsx-wld01-01a']

vcfWldList = [None]

hostList = {
    f'esx-0{i}a.site-a.vcf.lab': 
    {
        'config': {
            'username': esxUsername,
            'password': esxPassword
        }
    }
    for i in range(1, 8)
}



## MAIN

shutdownList = {}

token = fleet.getEncodedToken(lcmUsername, lcmPassword)

if debug:
    print(token)
    print(json.dumps(fleet.getAllEnvironments(lcmFqdn, token, sslVerify), indent=4))

try:
    print(f"INFO: Shutting down Cloud Management via Fleet Management.")

    start = time.time()
    print(f"START: {time.strftime('%H:%M:%S', time.localtime(start))}")

    envList = fleet.getAllEnvironments(lcmFqdn, token, sslVerify)

    shutdownEnv = ["vra","vrli"]

    # SYNCHRONIZE INVENTORY ALL ENVIRONMENTS IN FLEET MANAGEMENT

    for env in envList:
        productIds = envList[env]['products']
        fleet.triggerInventorySynch(lcmFqdn, token, sslVerify, env, productIds)

    # SHUTDOWN VMS IN ENVIRONMENTS

    for product in shutdownEnv:
        for env, details in envList.items():
            if product in details.get("products", []):
                print(env)
                fleet.triggerPowerEvent(lcmFqdn, token, sslVerify, env, product, "power-off")
                break

    # ADD WORKLOAD VMS TO SHUTDOWN LIST
    shutdownList = updateShutdownList(shutdownList, vcfWldList, hostList)

    print(f"TASK: Building a VM/Host Shutdown List - STARTED")


    # ADD WORKLOAD VCLI & K8S NODES VMS TO SHUTDOWN LIST
    if (core.isReachable(wldVcFqdn)):
        for pattern in patterns:
            wldRegexList = vmf.getVmsByRegex(wldVcFqdn, wldVcUsername, wldVcPassword, pattern)
            shutdownList = updateShutdownList(shutdownList, wldRegexList, hostList)
    else:
        print(f"ERROR: Unable to connect to {wldVcFqdn}.")
    
    # ADD MANAGEMENT VCLI & K8S NODES VMS TO SHUTDOWN LIST
    if (core.isReachable(mgmtVcFqdn)):
        for pattern in patterns:
            mgmtRegexList = vmf.getVmsByRegex(mgmtVcFqdn, mgmtVcUsername, mgmtVcPassword, pattern)
            shutdownList = updateShutdownList(shutdownList, mgmtRegexList, hostList)
    else:
        print(f"ERROR: Unable to connect to {mgmtVcFqdn}.")

    # ADD MGMT & NSX VMS TO SHUTDOWN LIST
    shutdownList = updateShutdownList(shutdownList, vcfMgmtList, hostList)
    shutdownList = updateShutdownList(shutdownList, vcfList, hostList)
    shutdownList = updateShutdownList(shutdownList, vksList, hostList)

    # add SEs to the list after Supervisors
    if (core.isReachable(wldVcFqdn)):
        for pattern in sepatterns:
            wldRegexList = vmf.getVmsByRegex(wldVcFqdn, wldVcUsername, wldVcPassword, pattern)
            shutdownList = updateShutdownList(shutdownList, wldRegexList, hostList)
    else:
        print(f"ERROR: Unable to connect to {wldVcFqdn}.")

    shutdownList = updateShutdownList(shutdownList, vcfNsxList, hostList)
    
    if len(shutdownList) > 0:
        print(f"TASK: Building a VM/Host Shutdown List - COMPLETED")
        file.createFile("shutdown.json", json.dumps(shutdownList, indent=4))
    else:
        raise SystemExit(f"ERROR: Shutdown List is empty.")

    if debug:
        print(json.dumps(shutdownList, indent=4))

    print("INFO: VM Shutdown Process - STARTED")
    
    # SHUTDOWN VMS IN SHUTDOWN LIST
    try:
        if len(shutdownList) > 0 :
            for vm in shutdownList:
                user = shutdownList[vm]['config']['username']
                password = shutdownList[vm]['config']['password']
                host = shutdownList[vm]['config']['host']

                print(f"TASK: Shutting Down {vm} on {host}.")
                
                vmf.shutdownVm(host, user, password, vm)
                core.countdown(5,1)

    except Exception as e:
        print(f"ERROR: {e}")
    
    print("INFO: VM Shutdown Process - COMPLETED")

    # RUN VSISH CMD ON HOSTS IN HOST LIST
    try:
        if len(hostList) > 0:
            for host in hostList:
                username = hostList[host]['config']['username']
                password = hostList[host]['config']['password']
                print(f"TASK: Running VSISH Command on '{host}'.")
                core.runRemoteScript(host, username, password, "yes | vsish -e set /config/LSOM/intOpts/plogRunElevator 1")

            print(f"INFO: Waiting for {vSanTimeout/60} mins for VSAN I/O to stop...")
            core.countdown(vSanTimeout, 60)
            
            for host in hostList:
                username = hostList[host]['config']['username']
                password = hostList[host]['config']['password']
                print(f"TASK: Running VSISH Command on '{host}'.")
                core.runRemoteScript(host, username, password, "yes | vsish -e set /config/LSOM/intOpts/plogRunElevator 0")

    except Exception as e:
        print(f"ERROR: {e}")

    # SHUTDOWN HOSTS IN HOST LIST
    
    try:
        if len(hostList) > 0:
            print("TASK: HOST Shutdown Process - STARTED")
            for host in hostList:
                username = hostList[host]['config']['username']
                password = hostList[host]['config']['password']
                vmf.shutdownHost(host, username, password)
            print("INFO: HOST Shutdown Process - COMPLETED")
        else:
            print("INFO: No Hosts in Host List.")
    except Exception as e:
        print(f"ERROR: {e}")

except Exception as e:
    print(f"ERROR: {e}")

finally:
    finish = time.time()
    print(f"END: {time.strftime('%H:%M:%S', time.localtime(finish))}")

    elapsed = finish - start
    print(f"ELAPSED: {time.strftime('%H:%M:%S', time.gmtime(elapsed))}")
