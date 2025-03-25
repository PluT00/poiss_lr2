from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.log import setLogLevel

class LinuxRouter(Node):
    def config(self, **params):
        super(LinuxRouter, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl net.ipv4.ip_forward=0')
        super(LinuxRouter, self).terminate()

class MyTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        s1 = self.addHost('s1')
        r1 = self.addNode('r1', cls=LinuxRouter)
        r2 = self.addNode('r2', cls=LinuxRouter)

        self.addLink(h1, r1)  # h1-eth0 <-> r1-eth0
        self.addLink(h2, r1)  # h2-eth0 <-> r1-eth1
        self.addLink(r1, r2)  # r1-eth2 <-> r2-eth0
        self.addLink(r2, h3)  # r2-eth1 <-> h3-eth0
        self.addLink(r2, s1)  # r2-eth2 <-> s1-eth0

def setup_network():
    topo = MyTopo()
    net = Mininet(topo=topo)
    net.start()

    # IP Configuration
    net['h1'].cmd('ifconfig h1-eth0 10.0.1.1/24 up')
    net['h2'].cmd('ifconfig h2-eth0 10.0.1.2/24 up')
    net['r1'].cmd('ifconfig r1-eth0 10.0.1.254/24 up')
    net['r1'].cmd('ifconfig r1-eth1 10.0.1.254/24 up')  # Same IP for h2
    net['r1'].cmd('ifconfig r1-eth2 10.0.2.1/24 up')
    net['r2'].cmd('ifconfig r2-eth0 10.0.2.2/24 up')
    net['r2'].cmd('ifconfig r2-eth1 10.0.3.254/24 up')  # Same IP for h3
    net['r2'].cmd('ifconfig r2-eth2 10.0.3.254/24 up')
    net['h3'].cmd('ifconfig h3-eth0 10.0.3.1/24 up')
    net['s1'].cmd('ifconfig s1-eth0 10.0.3.2/24 up')

    # Ensure interfaces are up
    net['r1'].cmd('ip link set r1-eth1 up')
    net['r2'].cmd('ip link set r2-eth1 up')

    # Routing Configuration with verification
    net['h1'].cmd('ip route add default via 10.0.1.254 || echo "h1 route failed"')
    net['h2'].cmd('ip route add default via 10.0.1.254 || echo "h2 route failed"')
    net['h3'].cmd('ip route add default via 10.0.3.254 || echo "h3 route failed"')
    net['s1'].cmd('ip route add default via 10.0.3.254 || echo "s1 route failed"')
    net['r1'].cmd('ip route add 10.0.3.0/24 via 10.0.2.2 || echo "r1 route failed"')
    net['r2'].cmd('ip route add 10.0.1.0/24 via 10.0.2.1 || echo "r2 route failed"')

    # Test Connectivity
    print("h1 -> r1:")
    print(net['h1'].cmd('ping -c 4 10.0.1.254'))
    print("h2 -> r1:")
    print(net['h2'].cmd('ping -c 4 10.0.1.254'))
    print("h3 -> r2:")
    print(net['h3'].cmd('ping -c 4 10.0.3.254'))
    print("r2 -> s1:")
    print(net['r2'].cmd('ping -c 4 10.0.3.2'))
    print("h1 -> s1:")
    print(net['h1'].cmd('ping -c 4 10.0.3.2'))

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup_network()