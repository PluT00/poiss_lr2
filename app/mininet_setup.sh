h1 ifconfig h1-eth0 10.0.1.1/24
h2 ifconfig h2-eth0 10.0.1.2/24
r1 ifconfig r1-eth0 10.0.1.254/24
r1 ifconfig r1-eth2 10.0.2.1/24
r2 ifconfig r2-eth0 10.0.2.2/24
r2 ifconfig r2-eth2 10.0.3.254/24
h3 ifconfig h3-eth0 10.0.3.1/24
s1 ifconfig s1-eth0 10.0.3.2/24

h1 ip route add default via 10.0.1.254
h2 ip route add default via 10.0.1.254
h3 ip route add default via 10.0.3.254
s1 ip route add default via 10.0.3.254
r1 ip route add 10.0.3.0/24 via 10.0.2.2
r2 ip route add 10.0.1.0/24 via 10.0.2.1

# После настройки

h1 ping 10.0.3.2