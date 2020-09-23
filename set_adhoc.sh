#! /bin/bash

function get_ip
{
	IFS=':' read -a ARRAY <<< $MAC
	
	IP1="$(echo $((16#${ARRAY[3]})) )"
	IP2="$(echo $((16#${ARRAY[4]})) )"
	IP3="$(echo $((16#${ARRAY[5]})) )"
	
	IP="${IPNET}.${IP1}.${IP2}.${IP3}"
}

function reset_wifi
{
 	
	sudo cp /etc/network/interfaces.orig /etc/network/interfaces

	sudo ifdown wlan0
	sudo ifup wlan0
}

function set_adhoc
{
	sudo ifconfig wlan0 down
	sudo iwconfig wlan0 mode ad-hoc
	sudo iwconfig wlan0 essid "gps_mesh"
	sudo iwconfig wlan0 key aaaaa11111
	sudo ip link set wlan0 up
	sudo ip addr add $IP/8 dev wlan0
}

function set_addrss
{
	sed -i "s/#IP/${IP}/g" adhoc_interface
	sed -i "s/#BROADCAST/${BROADCAST}/g" adhoc_interface
}

IP=""
IPNET="10"
CHANNEL="1"
BROADCAST="255.255.225.0"
MAC="$(ifconfig -a | grep HWaddr | awk 'NR==1{print $NF}')"

if [[ -n "${MAC}" ]]; then
	get_ip
	echo "MAC to IP resolved: ${IP}"
else
	echo "No MAC address available"
fi

#set_addrss
set_adhoc
#reset_wifi
