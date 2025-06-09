def main():
    # install forgotten pip package
    import subprocess
    import sys
    sys.path.append('/hol')
    import lsfunctions as lsf
    import os
    import requests
    import json
    os.umask(0o0000)  ## lsfunctions sets a umask without execute, need to override or script-running things will die
    os.environ["http_proxy"] = "http://proxy:3128"
    os.environ["https_proxy"] = "http://proxy:3128"
    os.environ["no_proxy"] = "localhost,127.0.0.0/8,::1,vcf.sddc.lab,10.0.0.87,10.0.1.87,10.0.0.0/8"
    os.environ["HTTP_PROXY"] = "http://proxy:3128"
    os.environ["HTTPS_PROXY"] = "http://proxy:3128"
    os.environ["NO_PROXY"] = "localhost,127.0.0.0/8,::1,vcf.sddc.lab,10.0.0.87,10.0.1.87,10.0.0.0/8"  

    # try:
    #     lsf.write_output("Configuring NSX T App profiles")   
    #     #add fast tcp and udp nsxt lb app profiles
    #     #prepare the http connection to NSX Manager
    #     session = requests.Session()
    #     session.verify = False
    #     session.auth = ('admin', 'VMware123!VMware123!')
    #     nsx_mgr = 'https://nsxmgr-01a.vcf.sddc.lab'
    #     fast_tcp_data = {
    #         'display_name': 'custom-fast-tcp',
    #         'idle_timeout': '1700',
    #         'close_timeout': '8',
    #         'resource_type': 'LBFastTcpProfile'
    #         }
    #     fast_udp_data = {
    #         'display_name' : 'custom-fast-udp',
    #         'idle_timeout':  '330',
    #         'resource_type': 'LBFastUdpProfile'
    #         }
    #     tcp_result = session.put(f"{nsx_mgr}/policy/api/v1/infra/lb-app-profiles/custom-fast-tcp", json=fast_tcp_data)
    #     lsf.write_output(f"Result code - {tcp_result.status_code}, Error text - {tcp_result.text}")
    #     udp_result = session.put(f"{nsx_mgr}/policy/api/v1/infra/lb-app-profiles/custom-fast-udp", json=fast_udp_data)
    #     lsf.write_output(f"Result code - {udp_result.status_code}, Error text - {udp_result.text}")
    # except Exception as e:
    #     lsf.write_output(e)
    #     try:
    #         lsf.write_output(e.stdout)
    #         lsf.write_output(e.stderr)
    #     except:
    #         pass 
    #     lsf.write_output('Adjustomatic failed at nsxt app profile create')   
    #     #lsf.labfail('Adjustomatic failed at nsxt app profile create')

    # try:
    #     lsf.write_output("Running final stages playbook")   
    #     # Playbook to run final config steps
    #     result = subprocess.run(["/home/holuser/.local/bin/ansible-playbook", "/vpodrepo/2025-labs/2571/HOL-2x71/2x71_podsetup/labconfig_finalstage.yaml", 
    #         "-i", "/vpodrepo/2025-labs/2571/HOL-2x71/2x71_podsetup/inventory.yml", "--vault-password-file", 
    #         "/vpodrepo/2025-labs/2571/HOL-2x71/2x71_podsetup/vaultsecret.txt"], capture_output=True, text=True, check=True)
    #     lsf.write_output(result)
    #     try:
    #         lsf.write_output(result.stdout)
    #     except:
    #         pass
    # except Exception as e:
    #     lsf.write_output(e)
    #     try:
    #         lsf.write_output(e.stdout)
    #         lsf.write_output(e.stderr)
    #     except:
    #         pass   
    #     lsf.write_output('Adjustomatic failed at avitweaker') 
    #     lsf.labfail('Adjustomatic failed at avitweaker')

    # try:
    #     stdout = subprocess.run(["/usr/bin/rm", "-rf", "/vpodrepo/2025-labs/2571/HOL-2x71/2x71_podsetup/vaultsecret.txt"], text=True, check=True)
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