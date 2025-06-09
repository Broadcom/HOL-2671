#!/bin/sh

# DEFAULT HOL FIREWALL RULESET
# version 16:15 MST 2019-12-13

# clear any existing rules
iptables --flush

#set the default policy on FORWARD to DROP
iptables -P FORWARD DROP

# EXAMPLE allow SSH: do not use as-is. Too open!
#iptables -A FORWARD -s 192.168.110.0/24 -p TCP --dport 22 -j ACCEPT

# allow IP inside the vPod, only on private networks
iptables -A FORWARD -s 192.168.0.0/16 -d 192.168.0.0/16 -j ACCEPT
iptables -A FORWARD -s 192.168.0.0/16 -d 172.16.0.0/12  -j ACCEPT
iptables -A FORWARD -s 192.168.0.0/16 -d 10.0.0.0/8     -j ACCEPT
iptables -A FORWARD -s 172.16.0.0/12 -d 192.168.0.0/16  -j ACCEPT
iptables -A FORWARD -s 172.16.0.0/12 -d 172.16.0.0/12   -j ACCEPT
iptables -A FORWARD -s 172.16.0.0/12 -d 10.0.0.0/8      -j ACCEPT
iptables -A FORWARD -s 10.0.0.0/8 -d 192.168.0.0/16     -j ACCEPT
iptables -A FORWARD -s 10.0.0.0/8 -d 172.16.0.0/12      -j ACCEPT
iptables -A FORWARD -s 10.0.0.0/8 -d 10.0.0.0/8         -j ACCEPT


# allow access to and from Google DNS
iptables -A FORWARD -p UDP -d 8.8.8.8 --dport 53 -j ACCEPT
iptables -A FORWARD -p UDP -s 8.8.8.8 --sport 53 -j ACCEPT
iptables -A FORWARD -p UDP -d 8.8.4.4 --dport 53 -j ACCEPT
iptables -A FORWARD -p UDP -s 8.8.4.4 --sport 53 -j ACCEPT

# allow RDP requests so captains don't need to disable the firewall
iptables -A FORWARD -p TCP --dport 3389 -j ACCEPT
iptables -A FORWARD -p TCP --sport 3389 -j ACCEPT

# allow ping everywhere
iptables -A FORWARD -p icmp --icmp-type 8 -s 0/0 -d 0/0 -m state --state NEW,ESTABLISHED,RELATED -j ACCEPT
iptables -A FORWARD -p icmp --icmp-type 0 -s 0/0 -d 0/0 -m state --state ESTABLISHED,RELATED -j ACCEPT

### LAB-SPECIFIC RULES

## TAC Helm repo IP
iptables -A FORWARD -p tcp -d 3.212.103.32 --dport 443 -j ACCEPT
iptables -A FORWARD -p tcp -s 3.212.103.32 --sport 443 -j ACCEPT

# Static IPs for the TAC Helm repo

iptables -A FORWARD -p tcp -d 107.23.45.255 --dport 443 -j ACCEPT
iptables -A FORWARD -p tcp -s 107.23.45.255 --sport 443 -j ACCEPT

iptables -A FORWARD -p tcp -d 3.92.113.83 --dport 443 -j ACCEPT
iptables -A FORWARD -p tcp -s 3.92.113.83 --sport 443 -j ACCEPT

iptables -A FORWARD -p tcp -d 52.7.76.205 --dport 443 -j ACCEPT
iptables -A FORWARD -p tcp -s 52.7.76.205 --sport 443 -j ACCEPT

# Bitnami.com
iptables -A FORWARD -p tcp -d 50.17.235.25 --dport 443 -j ACCEPT
iptables -A FORWARD -p tcp -s 50.17.235.25 --sport 443 -j ACCEPT

#   a104-92-253-81.deploy.static.akamaitechnologies.com.https:
iptables -A FORWARD -p tcp -d 104.92.253.81 --dport 443 -j ACCEPT
iptables -A FORWARD -p tcp -s 104.92.253.81 --sport 443 -j ACCEPT

# another ip for helm repo , just in case
iptables -A FORWARD -p tcp -d 23.198.162.207 --dport 443 -j ACCEPT
iptables -A FORWARD -p tcp -s 23.198.162.207 --dport 443 -j ACCEPT

### END RULES

# indicate that iptables has run
> ~holuser/firewall
