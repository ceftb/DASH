set ns [new Simulator]

# Include file that enables use of testbed specific commands
source tb_compat.tcl

# Declare variable that refers to the MAGI start command (which installs MAGI 
# and supporting tools on specified node at startup)
set magi_start "sudo python /share/magi/current/magi_bootstrap.py"

set victim [$ns node]

# Install MAGI and supporting tools on victim node at startup
tb-set-node-startcmd $victim "$magi_start"

set router [$ns node]
tb-set-node-startcmd $router "$magi_start"

set isp [$ns node]
tb-set-node-startcmd $isp "$magi_start"

set as1 [$ns node]
tb-set-node-startcmd $as1 "$magi_start"

set client1 [$ns node]
tb-set-node-startcmd $client1 "$magi_start"

set attacker1 [$ns node]
tb-set-node-startcmd $attacker1 "$magi_start"

# End defining nodes in topology

# Begin defining links between nodes

# Create duplex link between victim and router node with bandwidth 50 Mbps 
# and latency 1 ms and define variable that references this duplex link.
set vctmRtrLink [$ns duplex-link $victim $router 50Mbps 0ms DropTail]

# Set duplex link $vctmRtrLink to have loss of 0%. Behind the scenes, the
# DeterLab simulator will insert a singe delay node into this link to
# implement link loss functionality.
tb-set-link-loss $vctmRtrLink 0.0001

set rtrISPLink [$ns duplex-link $router $isp 25Mbps 100ms DropTail]
tb-set-link-loss $rtrISPLink 0.0001

set ispAS1Link [$ns duplex-link $isp $as1 1Gbps 100ms DropTail]
tb-set-link-loss $ispAS1Link 0.0001

set as1Client1Link [$ns duplex-link $as1 $client1 25Mbps 100ms DropTail]
tb-set-link-loss $as1Client1Link 0.0001

set as1Attacker1Link [$ns duplex-link $as1 $attacker1 25Mbps 100ms DropTail]
tb-set-link-loss $as1Attacker1Link 0.0001

# End defining links between nodes

# Set the desired OS on nodes. If unspecified, the default OS is Ubuntu1604-STD

# Automatically set up routing on nodes that run OSes provided by DeterLab.
# "Static" is the protocolOption argument to the "rtproto" command which 
# provides automatic routing support via static routing. Routes are 
# precomputed by a distributed route computation algorithm running in 
# parallel on experiment nodes.
$ns rtproto Static

# Start simulator
$ns run
