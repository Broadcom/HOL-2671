#!/bin/bash
ssh root@k8smaster-01a -o ConnectTimeout=5 'sudo shutdown -h now'
ssh root@k8smaster-01b -o ConnectTimeout=5 'sudo shutdown -h now'
ssh root@k8sworker-01a -o ConnectTimeout=5 'sudo shutdown -h now'
ssh root@k8sworker-02a -o ConnectTimeout=5 'sudo shutdown -h now'
ssh root@k8sworker-01b -o ConnectTimeout=5 'sudo shutdown -h now'
ssh root@k8sworker-02b -o ConnectTimeout=5 'sudo shutdown -h now'
echo "sleeping 60 for k8s shutdown"
sleep 60
echo "shutdown avi controllers"
echo VMware123! | ssh admin@avicon-01a 'sudo -S shutdown -h now'
echo VMware123! | ssh admin@avicon-01b 'sudo -S shutdown -h now'
sleep 30
echo "shutting down esx nodes"
ssh root@esx-01a '/sbin/shutdown.sh'
ssh root@esx-02a '/sbin/shutdown.sh'
ssh root@esx-03a '/sbin/shutdown.sh'
ssh root@esx-04a '/sbin/shutdown.sh'
ssh root@esx-05a '/sbin/shutdown.sh'
ssh root@esx-06a '/sbin/shutdown.sh'
echo "sleeping 60 for straggler vm shutdown"
sleep 60
ssh root@esx-01a '/sbin/poweroff'
ssh root@esx-02a '/sbin/poweroff'
ssh root@esx-03a '/sbin/poweroff'
ssh root@esx-04a '/sbin/poweroff'
ssh root@esx-05a '/sbin/poweroff'
ssh root@esx-06a '/sbin/poweroff'
echo "shutting down NSX mgrs"
ssh root@nsxmgr-01a 'shutdown -h now'
echo "shutting down VCSAs"
ssh root@vcsa-01a 'init 0'
echo "sleeping 30 to give esx more time to go down before storage"
sleep 30
echo "shutting down freenas"
#ssh root@stgb-01a '/sbin/shutdown -p now'
ssh root@stg-02a '/sbin/shutdown -p now'
echo "shutting down VRA"
ssh root@vra-01a 'shutdown -h now'
echo "you need to manually kill vpod router from vcd"
