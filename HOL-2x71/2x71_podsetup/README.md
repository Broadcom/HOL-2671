These are all files related to setting up the pod infrastructure.  The Resources folder are the files necessary for labstartup.py.

Consolidating template:

from pwsh
Connect-CIServer -Server wdc-vcd03.oc.vmware.com -org wdc-vcd03-hol-dev-d
./vCD-consolidate-vapptemplate-vm.ps1
