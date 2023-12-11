#!/usr/bin/python

from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import Node
from mininet.log import setLogLevel, info
from mininet.cli import CLI

class LinuxRouter (Node):
    def config (self, **params):
        super (LinuxRouter, self).config (**params)
        self.cmd ('sysctl net.ipv4.ip_forward=1')

    def terminate (self):
        self.cmd ('sysctl net.ipv4.ip_forward=0')
        super (LinuxRouter, self).terminate ()

# build the entire network topology
class NetworkTopo (Topo):

    def build(self, **_opts):
        # add three routers
        r1 = self.addNode('r1', cls=LinuxRouter, ip='10.1.0.1/24')
        r2 = self.addNode('r2', cls=LinuxRouter, ip='10.2.0.1/24')
        r3 = self.addNode('r3', cls=LinuxRouter, ip='10.3.0.1/24')
        
        # add three switches
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        s3 = self.addSwitch('s3')
        
        # add three hosts
        h1 = self.addHost('h1', ip='10.1.0.100/24', defaultRoute='via 10.1.0.1')
        h2 = self.addHost('h2', ip='10.2.0.100/24', defaultRoute='via 10.2.0.1')
        h3 = self.addHost('h3', ip='10.3.0.100/24', defaultRoute='via 10.3.0.1')
        
        # connect hosts with corresponding switches
        self.addLink(h1, s1)
        self.addLink(h2, s2)
        self.addLink(h3, s3)

        # connect hosts with corresponding routers
        self.addLink(s1, r1, intfName2='r1-eth1', params2={'ip':'10.1.0.1/24'})
        self.addLink(s2, r2, intfName2='r2-eth1', params2={'ip':'10.2.0.1/24'})
        self.addLink(s3, r3, intfName2='r3-eth1', params2={'ip':'10.3.0.1/24'})
        
        
        # connect routers pair by pair
        self.addLink('r1', 'r2', intfName1='r12', intfName2='r21',
                     params1={'ip': '10.12.0.1/24'}, params2={'ip': '10.12.0.2/24'})
        self.addLink('r1', 'r3', intfName1='r13', intfName2='r31',
                     params1={'ip': '10.13.0.1/24'}, params2={'ip': '10.13.0.3/24'})
        self.addLink('r3', 'r2', intfName1='r32', intfName2='r23',
                     params1={'ip': '10.23.0.3/24'}, params2={'ip': '10.23.0.2/24'})
        
def run():
    # create the network object from this topology
    net = Mininet(topo=NetworkTopo())
    
    # add NAT to let mininet subnets able to talk with outside network
    net.addNAT(name='nat1', ip='10.0.42.1').configDefault()
    net.addLink(net['r3'], net['nat1'],
                intfName1='r3-nat1', params1={'ip':'10.0.41.1/24'},
                intfName2='nat1-r3', params2={'ip':'10.0.41.2/24'})
    # set route tablef for nat1
    info(net['nat1'].cmd('ip route add 10.1.0.0/24 via 10.0.41.1 dev nat1-r3'))
    info(net['nat1'].cmd('ip route add 10.2.0.0/24 via 10.0.41.1 dev nat1-r3'))
    info(net['nat1'].cmd('ip route add 10.3.0.0/24 via 10.0.41.1 dev nat1-r3'))
    info(net['nat1'].cmd('ip route add default via 192.168.100.2 dev vxlan0'))
    info(net['nat1'].cmd('iptables -D FORWARD -i nat1-eth0 -d 10.0.0.0/8 -j DROP'))
    # set route tables for r1
    info(net['r1'].cmd('ip route add 10.2.0.0/24 via 10.12.0.2 dev r12'))
    info(net['r1'].cmd('ip route add 10.3.0.0/24 via 10.13.0.3 dev r13'))
    info(net['r1'].cmd('ip route add 10.0.42.0/24 via 10.13.0.3 dev r13'))
    info(net['r1'].cmd('ip route add default via 10.12.0.2 dev r12'))
    # set route tables for r2
    info(net['r2'].cmd('ip route add 10.1.0.0/24 via 10.12.0.1 dev r21'))
    info(net['r2'].cmd('ip route add 10.3.0.0/24 via 10.23.0.3 dev r23'))
    info(net['r2'].cmd('ip route add 10.0.42.0/24 via 10.23.0.3 dev r23'))
    info(net['r2'].cmd('ip route add default via 10.23.0.3 dev r23'))
    # set route tables for r3
    info(net['r3'].cmd('ip route add 10.1.0.0/24 via 10.13.0.1 dev r31'))
    info(net['r3'].cmd('ip route add 10.2.0.0/24 via 10.23.0.2 dev r32'))
    info(net['r3'].cmd('ip route add 10.0.42.0/24 via 10.0.41.2 dev r3-nat1'))
    info(net['r3'].cmd('ip route add default via 10.0.41.2 dev r3-nat1'))
    # set default route for hosts
    info(net['h1'].cmd('ip route add default via 10.1.0.1'))
    info(net['h2'].cmd('ip route add default via 10.2.0.1'))
    info(net['h3'].cmd('ip route add default via 10.3.0.1'))    
    
    
    info( '*** Starting network\n')
    net.start ()    
    info( '*** Running CLI\n' )
    CLI (net)
    info( '*** Stopping network' )
    net.stop ()


if __name__ == '__main__':
    setLogLevel('info')
    run()
