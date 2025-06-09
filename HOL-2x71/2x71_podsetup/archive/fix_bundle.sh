#!/bin/bash
sshpass -p "VMware1!" ssh root@192.168.110.1 'bash getrules.sh'
/usr/bin/python3 /hol/labupdater.py
