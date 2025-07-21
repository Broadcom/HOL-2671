#!/usr/bin/python3
import sys
sys.path.append('/hol')
import lsfunctions as lsf
import subprocess
from os.path import exists
import os
os.umask(0o0000) ## lsfunctions sets a umask without execute, need to override or script-running things will die

def main():  
    os.environ["http_proxy"] = "http://proxy:3128"
    os.environ["https_proxy"] = "http://proxy:3128"
    os.environ["no_proxy"] = "localhost,127.0.0.0/8,::1,site-a.vcf.lab,10.0.0.87,10.0.1.87,10.0.0.0/8"
    os.environ["HTTP_PROXY"] = "http://proxy:3128"
    os.environ["HTTPS_PROXY"] = "http://proxy:3128"
    os.environ["NO_PROXY"] = "localhost,127.0.0.0/8,::1,site-a.vcf.lab,10.0.0.87,10.0.1.87,10.0.0.0/8"  
    # try:
    #     lsf.write_output("Configuring avi license")   
    #     r = subprocess.run(["/home/holuser/.local/bin/ansible-playbook", 
    #         "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/labconfig_registration.yaml", "-i", 
    #         "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/inventory.yml", "--vault-password-file", 
    #         "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/vaultsecret.txt"], 
    #         capture_output=True, text=True, check=True)
    #     lsf.write_output(r)
    #     # with open('/vpodrepo/pod_registered.txt', 'w') as f:
    #     #     f.write('This pod has already run the registration , we wont run again')
    # except Exception as e:
    #     lsf.write_output(e)
    #     try:
    #         lsf.write_output(e.stdout)
    #         lsf.write_output(e.stderr)
    #     except:
    #         pass
    #     lsf.write_output('avi register playbook failed')
    #     lsf.labfail('Register wrapper failed')

    lsf.write_output("Running preliminary tasks")
    try:
        r = subprocess.run(["/home/holuser/.local/bin/ansible-playbook", 
            "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/labconfig_firststage.yaml", "-i", 
            "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/inventory.yml", "--vault-password-file", 
            "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/vaultsecret.txt"], 
            capture_output=True, text=True, check=True)
        lsf.write_output(r)
    except Exception as e:
        lsf.write_output(e)
        try:
            lsf.write_output(e.stdout)
            lsf.write_output(e.stderr)
        except:
            pass  
        lsf.write_output('preliminary tasks playbook failed')  
        lsf.labfail('preliminary tasks playbook failed')

    lsf.write_output("Configuring Site A Avi controller")
    try:
        r = subprocess.run(["/home/holuser/.local/bin/ansible-playbook", 
            "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/avi_configs/avi_config.yml", "-i", 
            "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/avi_configs/inv_sitea.yml", "--vault-password-file", 
             "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/vaultsecret.txt"], 
            capture_output=True, text=True, check=True)
        lsf.write_output(r)
    except Exception as e:
        lsf.write_output(e)
        try:
            lsf.write_output(e.stdout)
            lsf.write_output(e.stderr)
        except:
            pass  
        lsf.write_output('avi site A configuration failed')  
        lsf.labfail('avi site A configuration failed')
    #        
    lsf.write_output("Configuring Site B Avi controller")
    try:
        r = subprocess.run(["/home/holuser/.local/bin/ansible-playbook", 
            "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/avi_configs/avi_config.yml", "-i", 
            "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/avi_configs/inv_siteb.yml", "--vault-password-file", 
             "/vpodrepo/2025-labs/2671/HOL-2x71/2x71_podsetup/vaultsecret.txt"], 
            capture_output=True, text=True, check=True)
        lsf.write_output(r)
    except Exception as e:
        lsf.write_output(e)
        try:
            lsf.write_output(e.stdout)
            lsf.write_output(e.stderr)
        except:
            pass    
        lsf.write_output('avi site B configuration failed')
        lsf.labfail('avi site B configuration failed')


if __name__ == "__main__":
    if not exists("/vpodrepo/pod_registered.txt"):
        main()
    else:
        # this won't actually run in 2671, because the file write is commented out
        lsf.write_output("This pod has already run registration, not running again")


