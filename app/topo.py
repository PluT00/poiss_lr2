from mininet.topo import Topo
from mininet.node import Node

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

        self.addLink(h1, r1)
        self.addLink(h2, r1)
        self.addLink(r1, r2)
        self.addLink(r2, h3)
        self.addLink(r2, s1)

topos = {'mytopo': (lambda: MyTopo())}