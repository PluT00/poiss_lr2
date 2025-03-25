from mininet.net import Mininet
from mininet.node import Node
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.log import setLogLevel
import os

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

def setup_network():
    topo = MyTopo()
    net = Mininet(topo=topo)
    net.start()

    # Настройка IP-адресов
    net['h1'].cmd('ifconfig h1-eth0 10.0.1.1/24 up')
    net['h2'].cmd('ifconfig h2-eth0 10.0.1.2/24 up')
    net['r1'].cmd('ifconfig r1-eth0 10.0.1.254/24 up')
    net['r1'].cmd('ifconfig r1-eth1 10.0.1.253/24 up')
    net['r1'].cmd('ifconfig r1-eth2 10.0.2.1/24 up')
    net['r2'].cmd('ifconfig r2-eth0 10.0.2.2/24 up')
    net['r2'].cmd('ifconfig r2-eth1 10.0.3.253/24 up')
    net['r2'].cmd('ifconfig r2-eth2 10.0.3.254/24 up')
    net['h3'].cmd('ifconfig h3-eth0 10.0.3.1/24 up')
    net['s1'].cmd('ifconfig s1-eth0 10.0.3.2/24 up')

    # Настройка маршрутов
    net['h1'].cmd('ip route add default via 10.0.1.254')
    net['h2'].cmd('ip route add default via 10.0.1.253')
    net['h3'].cmd('ip route add default via 10.0.3.253')
    net['s1'].cmd('ip route add default via 10.0.3.254')
    net['r1'].cmd('ip route add 10.0.3.0/24 via 10.0.2.2')
    net['r2'].cmd('ip route add 10.0.1.0/24 via 10.0.2.1')

    # # Запуск iperf-сервера
    # net['s1'].cmd('iperf -s -u &')
    #
    # # Генерация трафика
    # net['h1'].cmd('iperf -c 10.0.3.2 -u -b 100k -p 5060 -t 20 &')
    # net['h2'].cmd('iperf -c 10.0.3.2 -u -b 1m -p 1935 -t 20 &')
    # net['h3'].cmd('iperf -c 10.0.3.2 -u -b 500k -p 80 -t 20 &')
    #
    # # Запуск QoS (если traffic_classifier скомпилирован)
    # os.system('sudo ./traffic_classifier &')
    #
    # # Проверка связи
    # print("Проверка пинга r2 -> s1:")
    # result = net['r2'].cmd('ping -c 4 10.0.3.2')
    # print(result)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup_network()