import requests
import json
import re
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import time
import base64
# import paramiko
import ssl
from pyVmomi import vim, vmodl
from  pyVim.connect import SmartConnect, Disconnect

import functions.core_functions as core

debug = False
sslVerify = False


def connect_vCenter(fqdn, username, password):
    context = ssl._create_unverified_context()
    try:
        print(f"INFO: Connecting to {fqdn} with {username}:{password}.")
        vc = SmartConnect(host=fqdn, user=username, pwd=password, port=443, sslContext=context)
    except Exception as e:
        print(f'ERROR: {e}')
        return None
    finally:
        return vc

def connect_host(fqdn, username, password):
    context = ssl._create_unverified_context()
    try:
        print(f"INFO: Connecting to {fqdn} with {username}:{password}.")
        context = ssl._create_unverified_context()
        vc = SmartConnect(host=fqdn, user=username, pwd=password, port=443, sslContext=context)
    except vim.fault.InvalidLogin as e:
        context = ssl._create_unverified_context()
        print(f"ERROR: Invalid login for {username} on {fqdn}.")
        print(f"INFO: Connecting to {fqdn} with {username}:None.")
        vc = SmartConnect(host=fqdn, user=username, pwd=None, port=443, sslContext=context)
    finally:
        return vc

def getVMbyName(fqdn, user, password, name):
    try:
        vc = connect_host(fqdn, user, password)
        content = vc.RetrieveContent()
        listOfVms = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        
    
        for vm in listOfVms.view:
            if vm.name == name:
                listOfVms.Destroy()
                return vm
        listOfVms.Destroy()
        return None
    except Exception as e:
        print(f"ERROR: {e}")

def getAllVms(fqdn, username, password):

    try:
        vc = connect_vCenter(fqdn, username, password)
        content = vc.RetrieveContent()

        listOfVms = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
           
        for vm in listOfVms.view:
            print(vm.name)
            listOfVms.Destroy()

        listOfVms.Destroy()
        return None    
    
    except Exception as e:
        print(f"ERROR: {e}")
    
    finally:
        return None
    

def isShutdown(vm):
    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOff:
        return True
    else:
        return False

def getVmsByRegex(fqdn, username, password, regex):

    try:
        vc = connect_vCenter(fqdn, username, password)
        content = vc.RetrieveContent()

        pattern = re.compile(regex)

        vmView = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)
        listOfVms = vmView.view
        vmView.Destroy()

        regexVms = []
        for vm in listOfVms:
            if pattern.match(vm.name):
                regexVms.append(vm.name)
    
    except Exception as e:
        print(f"ERROR: {e}")

    finally:
        return regexVms
    
def vmExists(fqdn, username, password, vmName):
    
    try:
        vc = connect_vCenter(fqdn, username, password)
        content = vc.RetrieveContent()
        listOfVms = content.viewManager.CreateContainerView(content.rootFolder, [vim.VirtualMachine], True)

        for vm in listOfVms.view:
            if (vm.name == vmName):
                listOfVms.Destroy()
                return vm
        
        listOfVms.Destroy()
        return None
    except Exception as e:
        print(f"ERROR: {e}")

def shutdownVm(fqdn, username, password, vm_name):
    try:
        vm = getVMbyName(fqdn, username, password, vm_name)

        if vm is not None:
            if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
                print(f"INFO: VMware Tools Status: \'{vm.guest.toolsRunningStatus}\' on {vm.name}.")
                print(f"INFO: Running Guest Shutdown on {vm.name}")
                try:
                    vm.ShutdownGuest()
                    while getVmToolsStatus(vm) != 'guestToolsNotRunning':
                        while vm.runtime.powerState != vim.VirtualMachinePowerState.poweredOff:
                            print(f"INFO: Waiting for Guest Shutdown on {vm.name}")
                            core.countdown(5,1)
                        else:
                            print(f"INFO: {vm.name} is powered off.")   
                except vim.fault.ToolsUnavailable as e:
                    print(f"INFO: Guest Shutdown on {vm.name} Failed. Powering Off")
                    powerOffVm(vm)
            else:
                print(f"INFO: {vm.name} is already powered off.")
        else:
            print(f"INFO: {vm.name} does not exist.")

    except Exception as e:
        print(f"ERROR: {e}")

def powerOffVm(vm):
    if vm.runtime.powerState == vim.VirtualMachinePowerState.poweredOn:
        try:
            task = vm.PowerOffVM_Task()
            while task.info.state == vim.TaskInfo.State.running:
                print(f"INFO: {vm.name} Power Off Task Progress: {task.info.progress if task.info.progress is not None else 'N/A'}%")
                core.countdown(5,1)
            if task.info.state == vim.TaskInfo.State.success:
                print(f"INFO: {vm.name} powered off successfully.")
            else:
                print(f"INFO: {vm.name} : Task failed {task.info.error}")
        except Exception as e:
            print(f"ERROR: {e}")
    else:
        print(f"INFO: VM {vm.name} already powered off.")

def monitorVmToolsStatus(vm, toolStatus):
    while getVmToolsStatus(vm) != toolStatus:
        core.countdown(5,1)
    print(f"INFO: VMware Tools Status: \'{vm.guest.toolsRunningStatus}\' on {vm.name}.")

def getVmToolsStatus(vm):
    print(f"INFO: VMware Tools Status: \'{vm.guest.toolsRunningStatus}\' on {vm.name}.")
    return vm.guest.toolsRunningStatus

def shutdownHost(fqdn, username, password):
    print(f"INFO: Shutting down {fqdn}...")

    try:
        if (core.isReachable(fqdn)):
            esx = connect_host(fqdn, username, password)
            content = esx.RetrieveContent()
            host = content.rootFolder.childEntity[0].hostFolder.childEntity[0].host[0]
        
            task = host.ShutdownHost_Task(force=True)
            while task.info.state == vim.TaskInfo.State.running:
                print(f"INFO: {host.name} Power Off Task Progress: {task.info.progress if task.info.progress is not None else 'N/A'}%")
                core.countdown(5,1)
            if task.info.state == vim.TaskInfo.State.success:
                print(f"INFO: {host.name} powered off successfully.")
            else:
                print(f"INFO: {host.name} : Task failed {task.info.error}")
        else:
            print(f"INFO: {fqdn} is not reachable.")
    except Exception as e:
        print(f"ERROR: {e}")