#!/bin/sh
# Simulates corporate firewall rules applied to agent sandbox (172.20.0.10)

# Default: block all outbound from agent except through proxy
iptables -I FORWARD -s 172.20.0.10 -j DROP

# Allow only proxy port
iptables -I FORWARD -s 172.20.0.10 -d 172.20.0.2 -p tcp --dport 8080 -j ACCEPT
iptables -I FORWARD -s 172.20.0.10 -d 172.20.0.2 -p tcp --dport 8443 -j ACCEPT

# Allow DNS only through corp DNS server
iptables -I FORWARD -s 172.20.0.10 -d 172.20.0.3 -p udp --dport 53 -j ACCEPT
iptables -I FORWARD -s 172.20.0.10 -d 172.20.0.3 -p tcp --dport 53 -j ACCEPT

# Block direct DNS to external resolvers (forces use of corp DNS)
iptables -I FORWARD -s 172.20.0.10 -p udp --dport 53 ! -d 172.20.0.3 -j DROP
iptables -I FORWARD -s 172.20.0.10 -p tcp --dport 53 ! -d 172.20.0.3 -j DROP

# Block common VPN/tunnel ports
iptables -I FORWARD -s 172.20.0.10 -p udp --dport 1194 -j DROP   # OpenVPN
iptables -I FORWARD -s 172.20.0.10 -p udp --dport 51820 -j DROP  # WireGuard
iptables -I FORWARD -s 172.20.0.10 -p tcp --dport 1080 -j DROP   # SOCKS
iptables -I FORWARD -s 172.20.0.10 -p tcp --dport 9050 -j DROP   # Tor

echo "Firewall rules applied"
tail -f /dev/null
