def main():
    # install forgotten pip package
    import subprocess
    import sys
    sys.path.append('/hol')
    sys.path.append('/home/holuser/py312venv/lib')
    import lsfunctions as lsf
    import os
    import requests
    import json
  
    os.umask(0o0000)  ## lsfunctions sets a umask without execute, need to override or script-running things will die
    password_file = "/home/holuser/creds.txt"
    os.environ["http_proxy"] = "http://proxy:3128"
    os.environ["https_proxy"] = "http://proxy:3128"
    os.environ["no_proxy"] = "localhost,127.0.0.0/8,::1,site-a.vcf.lab,10.1.1.90,10.0.0.0/8"
    os.environ["HTTP_PROXY"] = "http://proxy:3128"
    os.environ["HTTPS_PROXY"] = "http://proxy:3128"
    os.environ["NO_PROXY"] = "localhost,127.0.0.0/8,::1,site-a.vcf.lab,10.1.1.90,10.0.0.0/8"  
    os.environ["AVICTRL_PASSWORD"] = open(password_file, 'r').read()
    os.environ["TF_VAR_nsxt_password"] = open(password_file, 'r').read()

    try:
        lsf.write_output("Configuring NSX T App profiles")   
        #add fast tcp and udp nsxt lb app profiles
        #prepare the http connection to NSX Manager
        print(os.environ)
        lsf.write_output(os.environ)
        session = requests.Session()
        session.verify = False
        session.auth = ('admin', os.environ['AVICTRL_PASS'])
        nsx_mgr = 'https://nsx-wld01-a.site-a.vcf.lab'
        fast_tcp_data = {
            'display_name': 'custom-fast-tcp',
            'idle_timeout': '1700',
            'close_timeout': '8',
            'resource_type': 'LBFastTcpProfile'
            }
        fast_udp_data = {
            'display_name' : 'custom-fast-udp',
            'idle_timeout':  '330',
            'resource_type': 'LBFastUdpProfile'
            }
        tcp_result = session.put(f"{nsx_mgr}/policy/api/v1/infra/lb-app-profiles/custom-fast-tcp", json=fast_tcp_data)
        lsf.write_output(f"Result code - {tcp_result.status_code}, Error text - {tcp_result.text}")
        udp_result = session.put(f"{nsx_mgr}/policy/api/v1/infra/lb-app-profiles/custom-fast-udp", json=fast_udp_data)
        lsf.write_output(f"Result code - {udp_result.status_code}, Error text - {udp_result.text}")
    except Exception as e:
        lsf.write_output(e)
        try:
            lsf.write_output(e.stdout)
            lsf.write_output(e.stderr)
        except:
            pass 
        lsf.write_output('Adjustomatic failed at nsxt app profile create')   
        #lsf.labfail('Adjustomatic failed at nsxt app profile create')

    try:
        lsf.write_output("Running first stages playbook")   
        # Playbook to run final config steps
        result = subprocess.run(["/usr/bin/ansible-playbook", "/vpodrepo/2026-labs/2671/HOL-2x71/2x71_podsetup/labconfig_firststage.yaml", 
            "-i", "/vpodrepo/2026-labs/2671/HOL-2x71/2x71_podsetup/inventory.yml", "--vault-password-file", 
            "/home/holuser/vaultsecret.txt"], capture_output=True, text=True, check=True)
        lsf.write_output(result)
        try:
            lsf.write_output(result.stdout)
        except:
            pass
    except Exception as e:
        lsf.write_output(e)
        try:
            lsf.write_output(e.stdout)
            lsf.write_output(e.stderr)
        except:
            pass   
        lsf.write_output('Adjustomatic failed at avitweaker - first stage playbook step') 
        lsf.labfail('Adjustomatic failed at avitweaker - first stage playbook step')

    try:
        lsf.write_output("Running avi configuration playbook")   
        # Playbook to run final config steps
        result = subprocess.run(["/usr/bin/ansible-playbook", "/vpodrepo/2026-labs/2671/HOL-2x71/2x71_podsetup/avi_configs/avi_config.yml", 
            "-i", "/vpodrepo/2026-labs/2671/HOL-2x71/2x71_podsetup/avi_configs/inv_sitea.yml", "--vault-password-file", 
            "/home/holuser/vaultsecret.txt"], capture_output=True, text=True, check=True)
        lsf.write_output(result)
        try:
            lsf.write_output(result.stdout)
        except:
            pass
    except Exception as e:
        lsf.write_output(e)
        try:
            lsf.write_output(e.stdout)
            lsf.write_output(e.stderr)
        except:
            pass   
        lsf.write_output('Adjustomatic failed at avitweaker - avi configuration step') 
        lsf.labfail('Adjustomatic failed at avitweaker - avi configuration step')

    try:
        lsf.write_output("Running final stages playbook")   
        # Playbook to run final config steps
        result = subprocess.run(["/usr/bin/ansible-playbook", "/vpodrepo/2026-labs/2671/HOL-2x71/2x71_podsetup/labconfig_finalstage.yaml", 
            "-i", "/vpodrepo/2026-labs/2671/HOL-2x71/2x71_podsetup/inventory.yml", "--vault-password-file", 
            "/home/holuser/vaultsecret.txt"], capture_output=True, text=True, check=True)
        lsf.write_output(result)
        try:
            lsf.write_output(result.stdout)
        except:
            pass
    except Exception as e:
        lsf.write_output(e)
        try:
            lsf.write_output(e.stdout)
            lsf.write_output(e.stderr)
        except:
            pass   
        lsf.write_output('Adjustomatic failed at avitweaker - final stage playbook step') 
        lsf.labfail('Adjustomatic failed at avitweaker - final stage playbook step')

    # try:
    #     stdout = subprocess.run(["/usr/bin/rm", "-rf", "/home/holuser/vaultsecret.txt"], text=True, check=True)
    #     lsf.write_output(result)
    #     try:
    #         lsf.write_output(result.stdout)
    #     except:
    #         pass
    # except Exception as e:
    #     lsf.write_output(e)
    #     lsf.labfail('Adjustomatic failed at secret deletion')
    #     try:
    #         lsf.write_output(e.stderr)
    #     except:
    #         pass

    print("placeholder script, break glass for emergency")

if __name__ == "__main__":
    main()