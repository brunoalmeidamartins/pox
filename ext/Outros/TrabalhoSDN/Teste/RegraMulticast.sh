#!/bin/bash


ovs-ofctl del-flows s1
ovs-ofctl add-flow s1 dl_dst=00:00:00:00:01:01,actions=output:1
ovs-ofctl add-flow s1 dl_src=00:00:00:00:01:01,dl_dst=00:00:00:00:01:02,actions=output:2,12
ovs-ofctl add-flow s2 dl_src=00:00:00:00:01:01,dl_dst=00:00:00:00:01:02,actions=output:1
