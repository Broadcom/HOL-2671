#!/bin/bash
# chkconfig: 2345 20 80
# description: Description comes here....

# Source function library.

#ip link add dev sitea type vrf table 10

#ip link set dev sitea up

#ip link set dev sitea mtu 8000

#ip link add dev siteb type vrf table 20

#ip link set dev siteb up

#ip link set dev siteb mtu 8000

ip link set dev eth1 up && ip link set dev eth1 mtu 8000

ip link set dev eth2 up && ip link set dev eth2 mtu 8000

ip addr add 10.1.10.129/25 dev eth1

#ip route add default dev eth0 table 10

#ip route add default dev eth0 table 20

ip link add link eth1 name eth1.10 type vlan id 10 && ip link set dev eth1.10 up && ip link set dev eth1.10 mtu 8000 && ip addr add 10.1.1.1/24 dev eth1.10

ip link add link eth1 name eth1.11 type vlan id 11 && ip link set dev eth1.11 up && ip link set dev eth1.11 mtu 8000 && ip addr add 10.1.2.1/25 dev eth1.11

ip link add link eth1 name eth1.12 type vlan id 12 && ip link set dev eth1.12 up && ip link set dev eth1.12 mtu 8000 && ip addr add 10.1.2.129/25 dev eth1.12

ip link add link eth1 name eth1.13 type vlan id 13 && ip link set dev eth1.13 up && ip link set dev eth1.13 mtu 8000 && ip addr add 10.1.3.1/25 dev eth1.13

ip link add link eth1 name eth1.14 type vlan id 14 && ip link set dev eth1.14 up && ip link set dev eth1.14 mtu 8000 && ip addr add 10.1.3.129/25 dev eth1.14

ip link add link eth1 name eth1.15 type vlan id 15 && ip link set dev eth1.15 up && ip link set dev eth1.15 mtu 8000 && ip addr add 10.1.4.1/25 dev eth1.15

ip link add link eth1 name eth1.16 type vlan id 16 && ip link set dev eth1.16 up && ip link set dev eth1.16 mtu 8000 && ip addr add 10.1.4.129/25 dev eth1.16

ip link add link eth1 name eth1.17 type vlan id 17 && ip link set dev eth1.17 up && ip link set dev eth1.17 mtu 8000 && ip addr add 10.1.5.1/25 dev eth1.17

ip link add link eth1 name eth1.18 type vlan id 18 && ip link set dev eth1.18 up && ip link set dev eth1.18 mtu 8000 && ip addr add 10.1.5.129/25 dev eth1.18

#ip link add link eth1 name eth1.19 type vlan id 19 && ip link set dev eth1.19 master sitea && ip link set dev eth1.19 mtu 8000 && ip link set dev eth1.19 up && ip addr add 10.1.6.1/25 dev eth1.19 && ip route add 10.1.6.0/25 dev eth1.19

#ip link add link eth1 name eth1.20 type vlan id 20 && ip link set dev eth1.20 master sitea && ip link set dev eth1.20 mtu 8000 && ip link set dev eth1.20 up && ip addr add 10.1.6.129/25 dev eth1.20 && ip route add 10.1.6.128/25 dev eth1.20

ip link add link eth1 name eth1.19 type vlan id 19 && ip link set dev eth1.19 mtu 8000 && ip link set dev eth1.19 up && ip addr add 10.1.6.1/25 dev eth1.19 && ip route add 10.1.6.0/25 dev eth1.19

ip link add link eth1 name eth1.20 type vlan id 20 && ip link set dev eth1.20 mtu 8000 && ip link set dev eth1.20 up && ip addr add 10.1.6.129/25 dev eth1.20 && ip route add 10.1.6.128/25 dev eth1.20

ip link add link eth1 name eth1.21 type vlan id 21 && ip link set dev eth1.21 up && ip link set dev eth1.21 mtu 8000 && ip addr add 10.1.7.1/25 dev eth1.21

ip link add link eth1 name eth1.22 type vlan id 22 && ip link set dev eth1.22 up && ip link set dev eth1.22 mtu 8000 && ip addr add 10.1.7.129/25 dev eth1.22

ip link add link eth1 name eth1.23 type vlan id 23 && ip link set dev eth1.23 up && ip link set dev eth1.23 mtu 8000 && ip addr add 10.1.8.1/25 dev eth1.23

ip link add link eth1 name eth1.24 type vlan id 24 && ip link set dev eth1.24 up && ip link set dev eth1.24 mtu 8000 && ip addr add 10.1.8.129/25 dev eth1.24

ip link add link eth1 name eth1.25 type vlan id 25 && ip link set dev eth1.25 up && ip link set dev eth1.25 mtu 8000 && ip addr add 10.1.9.1/25 dev eth1.25

ip link add link eth1 name eth1.25 type vlan id 25 && ip link set dev eth1.25 up && ip link set dev eth1.25 mtu 8000 && ip addr add 10.1.9.1/25 dev eth1.25

ip link add link eth2 name eth2.40 type vlan id 40 && ip link set dev eth2.40 up && ip link set dev eth2.40 mtu 8000 && ip addr add 10.2.1.1/24 dev eth2.40

ip link add link eth2 name eth2.41 type vlan id 41 && ip link set dev eth2.41 up && ip link set dev eth2.41 mtu 8000 && ip addr add 10.2.2.1/25 dev eth2.41

ip link add link eth2 name eth2.42 type vlan id 42 && ip link set dev eth2.42 up && ip link set dev eth2.42 mtu 8000 && ip addr add 10.2.2.129/25 dev eth2.42

ip link add link eth2 name eth2.43 type vlan id 43 && ip link set dev eth2.43 up && ip link set dev eth2.43 mtu 8000 && ip addr add 10.2.3.1/25 dev eth2.43

ip link add link eth2 name eth2.44 type vlan id 44 && ip link set dev eth2.44 up && ip link set dev eth2.44 mtu 8000 && ip addr add 10.2.3.129/25 dev eth2.44

ip link add link eth2 name eth2.45 type vlan id 45 && ip link set dev eth2.45 up && ip link set dev eth2.45 mtu 8000 && ip addr add 10.2.4.1/25 dev eth2.45

ip link add link eth2 name eth2.46 type vlan id 46 && ip link set dev eth2.46 up && ip link set dev eth2.46 mtu 8000 && ip addr add 10.2.4.129/25 dev eth2.46

ip link add link eth2 name eth2.47 type vlan id 47 && ip link set dev eth2.47 up && ip link set dev eth2.47 mtu 8000 && ip addr add 10.2.5.1/25 dev eth2.47

ip link add link eth2 name eth2.48 type vlan id 48 && ip link set dev eth2.48 up && ip link set dev eth2.48 mtu 8000 && ip addr add 10.2.5.129/25 dev eth2.48

#ip link add link eth2 name eth2.49 type vlan id 49 && ip link set dev eth2.49 master siteb && ip link set dev eth2.49 mtu 8000 && ip link set dev eth2.49 up && ip addr add 10.2.6.1/25 dev eth2.49 && ip route add 10.2.6.0/25 dev eth2.49

#ip link add link eth2 name eth2.50 type vlan id 50 && ip link set dev eth2.50 master siteb && ip link set dev eth2.50 mtu 8000 && ip link set dev eth2.50 up && ip addr add 10.2.6.129/25 dev eth2.50 && ip route add 10.2.6.128/25 dev eth2.50

ip link add link eth2 name eth2.49 type vlan id 49 && ip link set dev eth2.49 mtu 8000 && ip link set dev eth2.49 up && ip addr add 10.2.6.1/25 dev eth2.49 && ip route add 10.2.6.0/25 dev eth2.49

ip link add link eth2 name eth2.50 type vlan id 50 && ip link set dev eth2.50 mtu 8000 && ip link set dev eth2.50 up && ip addr add 10.2.6.129/25 dev eth2.50 && ip route add 10.2.6.128/25 dev eth2.50

ip link add link eth2 name eth2.51 type vlan id 51 && ip link set dev eth2.51 up && ip link set dev eth2.51 mtu 8000 && ip addr add 10.2.7.1/25 dev eth2.51

ip link add link eth2 name eth2.52 type vlan id 52 && ip link set dev eth2.52 up && ip link set dev eth2.52 mtu 8000 && ip addr add 10.2.7.129/25 dev eth2.52

ip link add link eth2 name eth2.53 type vlan id 53 && ip link set dev eth2.53 up && ip link set dev eth2.53 mtu 8000 && ip addr add 10.2.8.1/25 dev eth2.53

ip link add link eth2 name eth2.54 type vlan id 54 && ip link set dev eth2.54 up && ip link set dev eth2.54 mtu 8000 && ip addr add 10.2.8.129/25 dev eth2.54

ip link add link eth2 name eth2.55 type vlan id 55 && ip link set dev eth2.55 up && ip link set dev eth2.55 mtu 8000 && ip addr add 10.2.9.1/25 dev eth2.55

ip link add link eth2 name eth2.56 type vlan id 56 && ip link set dev eth2.56 up && ip link set dev eth2.56 mtu 8000 && ip addr add 10.2.9.129/25 dev eth2.56

ip link add link eth2 name eth2.57 type vlan id 57 && ip link set dev eth2.57 up && ip link set dev eth2.57 mtu 8000 && ip addr add 10.2.10.1/25 dev eth2.57

ip link add link eth2 name eth2.58 type vlan id 58 && ip link set dev eth2.58 up && ip link set dev eth2.58 mtu 8000 && ip addr add 10.2.10.129/25 dev eth2.58

iptables -P INPUT ACCEPT

iptables -P OUTPUT ACCEPT

iptables -P FORWARD ACCEPT

iptables -A INPUT -p udp --dport 123 -j ACCEPT

iptables -A INPUT -p udp -m udp --dport 53 -j ACCEPT && iptables -A INPUT -p udp -m udp --dport 67 -j ACCEPT && iptables -A INPUT -p udp -m udp --dport 68 -j ACCEPT

iptables -A INPUT -p tcp -m tcp --dport 53 -j ACCEPT && iptables -A INPUT -p tcp -m tcp --dport 67 -j ACCEPT && iptables -A INPUT -p tcp -m tcp --dport 68 -j ACCEPT

iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

iptables -t nat -A POSTROUTING -o eth1 -j MASQUERADE

iptables -t nat -A POSTROUTING -o eth2 -j MASQUERADE

iptables -I INPUT -p tcp -m tcp --match multiport --dports 111,2049,20048 -j ACCEPT && iptables -I OUTPUT -p tcp -m tcp --match multiport --dports 111,2049,20048 -j ACCEPT

iptables -A INPUT -p tcp -m tcp --dport 179 -j ACCEPT

iptables -A INPUT -p tcp -m tcp --dport 2379:2380 -j ACCEPT

iptables -A INPUT -p tcp -m tcp --dport 4789 -j ACCEPT

iptables -A INPUT -p tcp -m tcp --dport 6443 -j ACCEPT

iptables -A INPUT -p tcp -m tcp --dport 3128 -j ACCEPT

iptables -A INPUT -p tcp -m tcp --dport 10250:10252 -j ACCEPT

iptables -A INPUT -p icmp --icmp-type echo-request -j ACCEPT

iptables-save > /etc/systemd/scripts/ip4save

#sleep 30
#/usr/sbin/sysctl -w net.ipv4.tcp_l3mdev_accept=1
#/usr/sbin/sysctl -w net.ipv4.udp_l3mdev_accept=1