#!/bin/bash
echo VMware1! | sshpass -p "VMware1!" ssh holuser@k8smaster-01a 'sudo -S shutdown -h now'
echo VMware1! | sshpass -p "VMware1!" ssh holuser@k8smaster-01b 'sudo -S shutdown -h now'
echo VMware1! | sshpass -p "VMware1!" ssh holuser@k8sworker-01a 'sudo -S shutdown -h now'
echo VMware1! | sshpass -p "VMware1!" ssh holuser@k8sworker-02a 'sudo -S shutdown -h now'
echo VMware1! | sshpass -p "VMware1!" ssh holuser@k8sworker-01b 'sudo -S shutdown -h now'
echo VMware1! | sshpass -p "VMware1!" ssh holuser@k8sworker-02b 'sudo -S shutdown -h now'
echo "sleeping 60 for k8s shutdown"
sleep 60
ssh root@esx-01a '/sbin/shutdown.sh'
ssh root@esx-02a '/sbin/shutdown.sh'
ssh root@esx-03a '/sbin/shutdown.sh'
ssh root@esx-01b '/sbin/shutdown.sh'
ssh root@esx-02b '/sbin/shutdown.sh'
ssh root@esx-03b '/sbin/shutdown.sh'
echo "sleeping 60 for straggler vm shutdown"
sleep 60
ssh root@esx-01a '/sbin/poweroff'
ssh root@esx-02a '/sbin/poweroff'
ssh root@esx-03a '/sbin/poweroff'
ssh root@esx-01b '/sbin/poweroff'
ssh root@esx-02b '/sbin/poweroff'
ssh root@esx-03b '/sbin/poweroff'
echo "shutdown avi controllers manuall"
#sshpass -p "VMware1!" ssh admin@avicon-01a 'sudo shutdown -h now'
#sshpass -p "VMware1!" ssh admin@avicon-01b 'sudo shutdown -h now'
echo "you need to manually kill vcsas and vpod router from vcd"
