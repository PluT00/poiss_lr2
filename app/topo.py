from mininet.topo import Topo
from mininet.node import OVSSwitch

class MyTopo(Topo):
    def build(self):
        h1 = self.addHost('h1')
        h2 = self.addHost('h2')
        h3 = self.addHost('h3')
        s1 = self.addHost('s1')
        r1 = self.addSwitch('r1', cls=OVSSwitch)
        r2 = self.addSwitch('r2', cls=OVSSwitch)

        self.addLink(h1, r1)
        self.addLink(h2, r1)
        self.addLink(r1, r2)
        self.addLink(r2, h3)
        self.addLink(r2, s1)

topos = {'mytopo': (lambda: MyTopo())}