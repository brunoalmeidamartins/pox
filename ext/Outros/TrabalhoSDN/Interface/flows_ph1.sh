#!/bin/bash

ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:01,actions=output:1
ovs-ofctl add-flow s1 dl_dst=00:00:00:00:00:02,actions=output:2
ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:03,actions=output:13
ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:04,actions=output:13
ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:11,actions=output:13
ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:12,actions=output:13
ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:03,actions=output:13
ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:04,actions=output:13
ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:11,actions=output:13
ovs-ofctl add-flow s1 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:12,actions=output:13

ovs-ofctl add-flow s2 dl_dst=00:00:00:00:00:03,actions=output:1
ovs-ofctl add-flow s2 dl_dst=00:00:00:00:00:04,actions=output:2
ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:01,actions=output:13
ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:02,actions=output:13
ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:11,actions=output:13
ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:12,actions=output:13
ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:01,actions=output:13
ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:02,actions=output:13
ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:11,actions=output:13
ovs-ofctl add-flow s2 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:12,actions=output:13

ovs-ofctl add-flow s3 dl_dst=00:00:00:00:00:11,actions=output:1
ovs-ofctl add-flow s3 dl_dst=00:00:00:00:00:12,actions=output:2
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:11,dl_dst=00:00:00:00:00:01,actions=output:11
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:11,dl_dst=00:00:00:00:00:02,actions=output:11
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:11,dl_dst=00:00:00:00:00:03,actions=output:12
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:11,dl_dst=00:00:00:00:00:04,actions=output:12
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:12,dl_dst=00:00:00:00:00:01,actions=output:11
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:12,dl_dst=00:00:00:00:00:02,actions=output:11
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:12,dl_dst=00:00:00:00:00:03,actions=output:12
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:12,dl_dst=00:00:00:00:00:04,actions=output:12
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:03,actions=output:12
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:01,dl_dst=00:00:00:00:00:04,actions=output:12
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:03,actions=output:12
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:02,dl_dst=00:00:00:00:00:04,actions=output:12
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:01,actions=output:11
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:03,dl_dst=00:00:00:00:00:02,actions=output:11
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:01,actions=output:11
ovs-ofctl add-flow s3 dl_src=00:00:00:00:00:04,dl_dst=00:00:00:00:00:02,actions=output:11

ovs-ofctl add-flow s4 dl_dst=00:00:00:00:00:01,actions=output:11
ovs-ofctl add-flow s4 dl_dst=00:00:00:00:00:02,actions=output:11
ovs-ofctl add-flow s4 dl_dst=00:00:00:00:00:03,actions=output:12
ovs-ofctl add-flow s4 dl_dst=00:00:00:00:00:04,actions=output:12
ovs-ofctl add-flow s4 dl_dst=00:00:00:00:00:11,actions=output:13
ovs-ofctl add-flow s4 dl_dst=00:00:00:00:00:12,actions=output:13
