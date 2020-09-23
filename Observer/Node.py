import sys
import time
import socket
import os
import json
from models import *

PORT = None
NODE_SEND = None


# uses bash commands to get IP. can't use socket library since that returns 127.0.1.1
BROADCAST = '10.255.255.255'
IP = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()

#uncomment if testing in 420 Lab
#BROADCAST = '140.160.137.255'
#IP = os.popen('ip addr show enp0s31f6 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()


class Node:
        def __init__(self, rport):
                self.ip = IP 
                self.port = rport
                self.server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self.client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                self.server.bind(('', rport))

        def get_ip(self):
                return self.ip


        def tcp_transfer(self, data, r_addr):
                sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sd.connect( (r_addr, 5005))
                sd.send(data)
                data = sd.recv(1024)
                sd.close()



        def send(self, message):
                json_msg = json.dumps(message.to_json())
                self.client.sendto(json_msg.encode('ascii'), (BROADCAST, self.port))

        def recv(self):
                msg, addr = self.server.recvfrom(1024)
                msg = json.loads(msg.decode('ascii'))

                if msg['pkt_type'] == "gps":
                        pkt = GPSPacket(msg['lat'], msg['lng'], json_pkt=msg)
                elif msg['pkt_type'] == "graph":
                        pkt = GraphPacket(msg['graph'], json_pkt=msg)
                elif msg['pkt_type'] == "message":
                        pkt = MessagePacket(msg["message"], json_pkt=msg)
                elif msg['pkt_type'] == "Hello":
                        pkt = Hello(json_pkt=msg) 
                elif msg['pkt_type'] == "query":
                        pkt = QueryPacket(msg['dst_ip'], msg['query_id'], msg['service'], interval=msg['interval'], json_pkt=msg, time=msg['time'], delta=msg['delta'])
 
                elif msg['pkt_type'] == "":
                        pkt = AckPacket(msg['dst_ip'], msg['query_id'], msg['service'], data=msg['data'], json_pkt=msg) 
                if not addr[0] == IP:
                        return (addr[0], pkt)


        def close(self):
                self.client.sock.close()
                self.server.sock.close()


