#!/bin/bash
echo "Not Reported" > /hol/vlp-cloud.txt
/usr/bin/cp /hol/gitrepos/python-labstartup/lab* /hol
/usr/bin/chmod +x /hol/lab*
/usr/bin/cp /hol/gitrepos/python-labstartup/lsfunctions.py /hol
/usr/bin/chmod +x /hol/lsfunctions.py
/usr/bin/cp -r /hol/gitrepos/python-labstartup/Tools /hol
#cd /hol/Tools
find /hol/Tools -type f \( -iname \*.py -o -iname \*.sh -o -iname \*.ps1 \) -exec /usr/bin/chmod {} \;
/usr/bin/cp -r /hol/gitrepos/python-labstartup/Startup /hol
#cd /hol/Startup
find /hol/Startup -type f \( -iname \*.py -o -iname \*.sh -o -iname \*.ps1 \) -exec /usr/bin/chmod {} \;
/usr/bin/cp /hol/gitrepos/python-labupdater/labup* /hol
/usr/bin/chmod +x /hol/labup*
/usr/bin/sed -i.bak s/HOL-BADSKU/HOL-2337/g /hol/labstartup.py
/usr/bin/sed -i -e '/ATTENTION/,+4 s/^/#/' /hol/labstartup.py 
