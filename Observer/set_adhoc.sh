#!/bin/bash

sudo service network-manager stop
sudo ip link set wlp12s0 down
sudo iwconfig wlp12s0 mode ad-hoc
sudo iwconfig wlp12s0 essid "gps_mesh"
sudo iwconfig wlp12s0 key aaaaa11111
sudo ip link set wlp12s0 up
sudo ip addr flush dev wlp12s0
sudo ip addr add 10.0.0.3/8 dev wlp12s0
