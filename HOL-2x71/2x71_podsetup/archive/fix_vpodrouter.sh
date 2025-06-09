#!/bin/bash
cat << EOF > /etc/sysctl.d/99-sysctl.conf
net.ipv4.ip_forward=1
net.ipv6.conf.all.forwarding=1
net.ipv4.conf.eth0.arp_announce=2
net.ipv4.conf.eth0.arp_ignore=1
net.ipv4.conf.eth1.arp_announce=2
net.ipv4.conf.eth1.arp_ignore=1
net.ipv4.conf.all.arp_ignore=1
net.ipv4.conf.default.arp_ignore=1
net.ipv4.conf.default.arp_announce=2
EOF
/usr/sbin/sysctl -p /etc/sysctl.d/99-sysctl.conf
/usr/bin/systemctl restart networking
