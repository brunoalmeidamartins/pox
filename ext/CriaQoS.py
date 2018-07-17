import os

#mypass = 'My mypassword'
mypass = "bruno270591"

def executaComandosOVS(comando):
    #print(comando)
    text = os.popen("echo %s | sudo -S %s" % (mypass, comando))
'''
a = 'ovs-vsctl --all destroy Queue' #Destroi todas as queue
b = 'ovs-vsctl --all destroy QoS' #Destroi todas as qos

#executaComandosOVS(b)
#executaComandosOVS(a)
'''
#comando = 'ovs-vsctl create qos type=linux-htb other-config:max-rate=40000000 queues=0=@comum,1=@unicast,2=@multicast -- --id=@comum create queue other-config:min-rate=10000000 other-config:max-rate=10000000 -- --id=@unicast create queue other-config:min-rate=20000000 other-config:max-rate=20000000 -- --id=@multicast create queue other-config:min-rate=10000000 other-config:max-rate=10000000'
comando1 = 'ovs-vsctl set port s1-eth13 qos=@pm -- --id=@pm create qos type=linux-htb other-config:max-rate=40000000 queues=0=@comum,1=@unicast,2=@multicast -- --id=@comum create queue other-config:min-rate=10000000 other-config:max-rate=10000000 -- --id=@unicast create queue other-config:min-rate=20000000 other-config:max-rate=20000000 -- --id=@multicast create queue other-config:min-rate=10000000 other-config:max-rate=10000000'
comando2 = 'ovs-vsctl set port s3-eth11 qos=@pm -- --id=@pm create qos type=linux-htb other-config:max-rate=40000000 queues=0=@comum,1=@unicast,2=@multicast -- --id=@comum create queue other-config:min-rate=10000000 other-config:max-rate=10000000 -- --id=@unicast create queue other-config:min-rate=20000000 other-config:max-rate=20000000 -- --id=@multicast create queue other-config:min-rate=10000000 other-config:max-rate=10000000'
comando3 = 'ovs-vsctl set port s3-eth12 qos=@pm -- --id=@pm create qos type=linux-htb other-config:max-rate=40000000 queues=0=@comum,1=@unicast,2=@multicast -- --id=@comum create queue other-config:min-rate=10000000 other-config:max-rate=10000000 -- --id=@unicast create queue other-config:min-rate=20000000 other-config:max-rate=20000000 -- --id=@multicast create queue other-config:min-rate=10000000 other-config:max-rate=10000000'
comando4 = 'ovs-vsctl set port s3-eth14 qos=@pm -- --id=@pm create qos type=linux-htb other-config:max-rate=40000000 queues=0=@comum,1=@unicast,2=@multicast -- --id=@comum create queue other-config:min-rate=10000000 other-config:max-rate=10000000 -- --id=@unicast create queue other-config:min-rate=20000000 other-config:max-rate=20000000 -- --id=@multicast create queue other-config:min-rate=10000000 other-config:max-rate=10000000'
comando5 = 'ovs-vsctl set port s2-eth13 qos=@pm -- --id=@pm create qos type=linux-htb other-config:max-rate=40000000 queues=0=@comum,1=@unicast,2=@multicast -- --id=@comum create queue other-config:min-rate=10000000 other-config:max-rate=10000000 -- --id=@unicast create queue other-config:min-rate=20000000 other-config:max-rate=20000000 -- --id=@multicast create queue other-config:min-rate=10000000 other-config:max-rate=10000000'
comando6 = 'ovs-vsctl set port s4-eth13 qos=@pm -- --id=@pm create qos type=linux-htb other-config:max-rate=40000000 queues=0=@comum,1=@unicast,2=@multicast -- --id=@comum create queue other-config:min-rate=10000000 other-config:max-rate=10000000 -- --id=@unicast create queue other-config:min-rate=20000000 other-config:max-rate=20000000 -- --id=@multicast create queue other-config:min-rate=10000000 other-config:max-rate=10000000'

executaComandosOVS(comando1)
executaComandosOVS(comando2)
executaComandosOVS(comando3)
executaComandosOVS(comando4)
executaComandosOVS(comando5)
executaComandosOVS(comando6)
#ovs-vsctl --all destroy qos #Destroi todas as qos

lista_switches = ['s1','s2','s4']
porta = ''
for i in lista_switches: #Somente os swtiches s1, s2, s3
    '''
    comando1 = 'ovs-ofctl add-flow '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.18,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando2 = 'ovs-ofctl add-flow '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.19,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando3 = 'ovs-ofctl add-flow '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.20,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando4 = 'ovs-ofctl add-flow '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.21,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando5 = 'ovs-ofctl add-flow '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.22,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando6 = 'ovs-ofctl add-flow '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.23,nw_proto=17,actions=enqueue:13:2'  #Multicast

    comando7 = 'ovs-ofctl add-flow '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.11,actions=enqueue:13:1' #unicast
    comando8 = 'ovs-ofctl add-flow '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.12,actions=enqueue:13:1' #unicast
    executaComandosOVS(comando1)
    executaComandosOVS(comando2)
    executaComandosOVS(comando3)
    executaComandosOVS(comando4)
    executaComandosOVS(comando5)
    executaComandosOVS(comando6)
    executaComandosOVS(comando7)
    executaComandosOVS(comando8)
    '''
    comando1 = 'ovs-ofctl mod-flows '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.18,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando2 = 'ovs-ofctl mod-flows '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.19,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando3 = 'ovs-ofctl mod-flows '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.20,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando4 = 'ovs-ofctl mod-flows '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.21,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando5 = 'ovs-ofctl mod-flows '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.22,nw_proto=17,actions=enqueue:13:2'  #Multicast
    comando6 = 'ovs-ofctl mod-flows '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.23,nw_proto=17,actions=enqueue:13:2'  #Multicast

    comando7 = 'ovs-ofctl mod-flows '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.11,actions=enqueue:13:1' #unicast
    comando8 = 'ovs-ofctl mod-flows '+i+' priority=50001,dl_type=0x0800,nw_dst=10.0.0.12,actions=enqueue:13:1' #unicast
    executaComandosOVS(comando1)
    executaComandosOVS(comando2)
    executaComandosOVS(comando3)
    executaComandosOVS(comando4)
    executaComandosOVS(comando5)
    executaComandosOVS(comando6)
    executaComandosOVS(comando7)
    executaComandosOVS(comando8)

lista_portas = ['11','12','14']
for i in lista_portas:
    '''
    comando1 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.18,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando2 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.19,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando3 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.20,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando4 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.21,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando5 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.22,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando6 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.23,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    executaComandosOVS(comando1)
    executaComandosOVS(comando2)
    executaComandosOVS(comando3)
    executaComandosOVS(comando4)
    executaComandosOVS(comando5)
    executaComandosOVS(comando6)
    '''
    comando1 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.18,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando2 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.19,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando3 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.20,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando4 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.21,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando5 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.22,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    comando6 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.23,nw_proto=17,actions=enqueue:'+i+':2'  #Multicast
    executaComandosOVS(comando1)
    executaComandosOVS(comando2)
    executaComandosOVS(comando3)
    executaComandosOVS(comando4)
    executaComandosOVS(comando5)
    executaComandosOVS(comando6)
'''
comando7 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.1,actions=enqueue:11:1' #unicast
comando8 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.2,actions=enqueue:11:1' #unicast

comando9 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.3,actions=enqueue:12:1' #unicast
comando10 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.4,actions=enqueue:12:1' #unicast

comando11 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.5,actions=enqueue:14:1' #unicast
comando12 = 'ovs-ofctl add-flow s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.6,actions=enqueue:14:1' #unicast

executaComandosOVS(comando7)
executaComandosOVS(comando8)
executaComandosOVS(comando9)
executaComandosOVS(comando10)
executaComandosOVS(comando11)
executaComandosOVS(comando12)
'''
comando7 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.1,actions=enqueue:11:1' #unicast
comando8 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.2,actions=enqueue:11:1' #unicast

comando9 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.3,actions=enqueue:12:1' #unicast
comando10 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.4,actions=enqueue:12:1' #unicast

comando11 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.5,actions=enqueue:14:1' #unicast
comando12 = 'ovs-ofctl mod-flows s3 priority=50001,dl_type=0x0800,nw_dst=10.0.0.6,actions=enqueue:14:1' #unicast

executaComandosOVS(comando7)
executaComandosOVS(comando8)
executaComandosOVS(comando9)
executaComandosOVS(comando10)
executaComandosOVS(comando11)
executaComandosOVS(comando12)

'''
ovs-ofctl
add-flow<bridge><match-field>actions=enqueue:<port>:<queue>
The port should be an OpenFlow port number or keyword(eg:LOCAL).This action means to
enqueue the packets on specified queue within the port.The queues numbers depend on switch.

ovs-ofctl
add-flow<bridge><match-field>actions=set_queue:<queue>
By taking this action, the packets that is output the port will be output the specified queue . Different
switch has different numbers of supported queues.

'''
