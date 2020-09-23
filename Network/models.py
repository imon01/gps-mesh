import json
import uuid
import copy
import socket
import datetime
import os
from const import *

IP = os.popen('ip addr show wlan0 | grep "\<inet\>" | awk \'{ print $2 }\' | awk -F "/" \'{ print $1 }\'').read().strip()

class BasePacket( object) :
        """
        Basic packet class. All other packet classes will inherit this class.
        """
        def __init__(self):
                """
                Constructor
                """
                self.ip = IP
                self.ttl = 30
                self.uuid = str(uuid.uuid1())
                self.timestamp = str(datetime.datetime.now())

        def to_json(self):
                """
                To JSON
                Returns JSON representation of packet. This method will be overloaded for new classes.
                :return: Dictionary representation of a packet.
                :rtype: dict
                """
                return {"ip": self.ip,"ttl":self.ttl, "uuid": self.uuid, "timestamp": self.timestamp}

class GPSPacket(BasePacket):
        """
        GPS Packet
        Class representation of a GPS packet.
        """
        def __init__(self, lat, lng, json_pkt=None):
                """
                Constructor
                Create a GPS Packet. If provided json_pkt, it will reconstruct
                the json_pkt into an object, otherwise it will generate a new
                packet.
                
                :param lat: (float) Latitude value
                :param lng: (float) Longitude value
                :param json_pkt: (dict) Packet to reconstruct
                """
                if json_pkt is None:
                        self.lat = lat
                        self.lng = lng
                        self.pkt_type = "gps" 
                        super(GPSPacket, self).__init__()
                else:
                        self.ip  = json_pkt["ip"] 
                        self.ttl = json_pkt["ttl"]
                        self.lng = json_pkt["lng"]
                        self.lat = json_pkt["lat"]
                        self.timestamp = json_pkt["timestamp"]
                        self.uuid = json_pkt["uuid"]
                        self.pkt_type = json_pkt["pkt_type"]

        def to_json(self):
                """
                To JSON
                Constructs JSON representation of packet.
                :return: Dictionary representation of packet.
                :rtype: dict
                """
                packet_json = super(GPSPacket, self).to_json()
                packet_json['lat'] = self.lat
                packet_json['lng'] = self.lng
                packet_json["pkt_type"] = self.pkt_type
                return packet_json

class GraphPacket(BasePacket):
        """
        Graph Packet
        Class representation of a Graph packet.
        """
        def __init__(self, graph, json_pkt=None):
                """
                Constructor
                Constructs an object representation of a Graph packet.
                If given json_pkt, it will reconstruct the packet based
                on the information in json_pkt. Otherwise, it will create
                a new packet.
                
                :param graph: (dict) Adjacency list of neighbor Pis
                :param json_pkt: (dict) JSON representation of a Graph packet
                """
                if json_pkt is None:
                        self.graph = graph
                        self.pkt_type = "graph"
                        super(GraphPacket, self).__init__()
                else:
                        self.ip  = json_pkt["ip"] 
                        self.ttl = json_pkt["ttl"]
                        self.timestamp = json_pkt["timestamp"]
                        self.uuid = json_pkt["uuid"]
                        self.graph = json_pkt["graph"]
                        self.pkt_type = json_pkt["pkt_type"]
            
        def to_json(self):
                """
                To JSON
                Creates a JSON representation of the current packet
                :return: Returns a dictionary represenation
                :rtype: dict
                """
                packet_json = super(GraphPacket, self).to_json()
                packet_json['graph'] = self.graph
                packet_json['pkt_type'] = self.pkt_type
                return packet_json

class MessagePacket(BasePacket):
        def __init__(self, message, json_pkt=None):
                """
                Message constructor
                
                Parameters
                message(str):
                json_pkt(json)
                
                Returns:
                MessagePacket
                """
                if json_pkt is None:
                        self.message = message
                        self.pkt_type = "message"
                        super(MessagePacket, self).__init__()
                else:
                        self.ip  = json_pkt["ip"] 
                        self.ttl = json_pkt["ttl"]
                        self.timestamp = json_pkt["timestamp"]
                        self.uuid = json_pkt["uuid"]
                        self.message = json_pkt["message"]
                        self.pkt_type = json_pkt['pkt_type']

        def to_json(self):

                """
                To JSON
                
                Translation of packet to JSON representation
                
                Parameters:
                Self
                
                Returns:
                dictionary
                
                """
                packet_json = super(MessagePacket, self).to_json()
                packet_json['message'] = self.message
                packet_json["pkt_type"] = self.pkt_type
                return packet_json

class QueryPacket(BasePacket):

        """
        QueryPacket for specific information.
        """
        def __init__(self, dst_ip, query_id, service, interval=None, json_pkt=None, time=None, delta=None):
        """

        Constructor for Query Packet. 

        Parameters:
        dest_ip(str): target ip in network
        query_id(str): query id for acknowleding queries
        service(enum): type of service requests
        interval(enum): time interval information of data request service
        json_pkt(json): conversion to query packet
        time(str): time for querying information
        delta(int): time window interval data pull service

        Returns:
        Query packet
        """
                if json_pkt is None:
                        self.dst_ip     = dst_ip
                        self.query_id   = query_id
                        self.pkt_type   = "query"
                        self.service    = service
                        super(QueryPacket, self).__init__()

                        if service == SERVICE.DATA:
                                self.interval = interval
                                
                                if interval == INTERVAL.FULL or interval == INTERVAL.CURR:
                                        self.time  = 0
                                        self.delta = 0

                                if delta is None:
                                        delta = 0

                                if interval == INTERVAL.INTVL or interval == INTERVAL.TIME:
                                        self.time = time
                                        self.delta = delta

                        #if service is SERVICE.NETSTAT network status
                                #do stuff here

                        #if service is SERVICE.GPSSTAT gps status
                                # do stuff here 
                        
                        super(QueryPacket, self).__init__()     
                else:
                        self.ip         = json_pkt['ip'] 
                        self.ttl        = json_pkt['ttl']
                        self.uuid       = json_pkt['uuid']
                        self.time       = json_pkt['time']
                        self.delta      = json_pkt['delta']
                        self.dst_ip     = json_pkt['dst_ip']
                        self.service    = json_pkt['service']
                        self.interval   = json_pkt['interval']
                        self.pkt_type   = json_pkt['pkt_type']
                        self.query_id   = json_pkt['query_id']
                        self.timestamp  = json_pkt["timestamp"]

        def to_json(self):
                """
                To JSON
                
                Translation of packet to JSON representation
                
                Parameters:
                Self
                
                Returns:
                dictionary
                
                """
                packet_json             = super(QueryPacket, self).to_json()
                packet_json['time']     = self.time
                packet_json['delta']    = self.delta
                packet_json['dst_ip']   = self.dst_ip
                packet_json['service']  = self.service
                packet_json['interval'] = self.interval
                packet_json['query_id'] = self.query_id
                packet_json["pkt_type"] = self.pkt_type
                return packet_json


#Acknowledgment packet for query packet
class AckPacket(BasePacket):
        """
        Query acknowledgement packet. 
        """
        
        def __init__(self, dst_ip, query_id, service, data=None, json_pkt=None):
                """
                
                Acknowledgement packet constructor
                
                Parameters:
                dst_ip(str): requesters destination address
                query_id(str): requester's query set id
                service(enum): type of service
                data(json comp): JSON library compatible formated data
                json_pkt(json comp):JSON library compatible formated data
                
                
                Returns:
                AckPacket
                
                """
                if json_pkt is None:
                        self.dst_ip     = dst_ip
                        self.query_id   = query_id
                        self.pkt_type   = "ack"

                        if service is SERVICE.DATA:
                                try:
                                        self.data = data
                                except:
                                        raise Exception("must provide data for Serivce data request")
                        
                        super(AckPacket, self).__init__()

                else:
                        self.ip         = json_pkt['ip']
                        self.ttl        = json_pkt['ttl']
                        self.uuid       = json_pkt['uuid']
                        self.data       = json_pkt['data']
                        self.dst_ip     = json_pkt['dst_up']
                        self.query_id   = json_pkt['query_id']
                        self.pkt_type   = json_pkt['pkt_type']
                        self.timestamp  = json_pkt['timestamp']

        def to_json(self):
                """
                To JSON
                
                Translation of packet to JSON representation
                
                Parameters:
                Self
                
                Returns:
                dictionary
                
                """
                packet_json     = super(AckPacket, self).to_json()
                packet_json['timestamp'] = self.timestamp
                packet_json['dst_ip']   = self.dst_ip
                packet_json['query_id'] = self.query_id
                packet_json['pkt_type'] = self.pkt_type
                return packet_json


class Graph:
        """

        Graph or Network tracking module. Used for P2P system.

        Remarks:
        Adjacency list constains list of immediate neighbhors
        Adjacnency tables are tables (ip, adjacency lists) pairs.
        uuid_packet used to save observed packet information

	Implementation:
	B-tree implementation of network. Each system node generates
	a unique B-tree on graph flush.
        """
def __init__(self, ip):
                """
                Initializes Graph option and sets local graph ip to IP
                
                Parameters:
                ip (string): 
                
                Returns:
                None    
                """
                self.ip = ip
                self.packet_table = { ip:{}}
                self.prev_packet_table = {}
                self.neighbors = []
                self.prev_neighbors = []
                self.adj_list = self.prev_neighbors
                self.adj_table = {ip: []}
                self.prev_adj_table = { ip:[]}  
                self.uuid_packet_cache = {}

        def add_vertex(self, v):
                self.adj_list.setdefault(v, [])

        def add_edge(self, v, e):
                try:
                        self.adj_list[v].append(e)
                except:
                        raise Exception("Vertex {} not found in graph".format(v))
        
        #
        # Remarks:
        #       -Store self packets
        #       
        def store(self, pkt):
                """
                
                Stores local system information. 
                
                Parameters:
                pkt(BasePacket): at a minimum, this is a base packet
                
                Returns:
                None    
                
                """
                self.uuid_packet_cache.setdefault( pkt.uuid, None)
                _uuid_table = self.packet_table[self.ip]
                
                #TODO: remove packet... if not used... mem issue
                _uuid_table.setdefault(pkt.uuid, None)


        # 
        # Remarks:
        #       -filter packets by looking at packet's uuid, store if new
        #
        def filter(self, pkt, sender):
                """
                
                Filters packet by packet's uuid field. Store if unobserved.
                
                
                Paramters:
                pkt (Packet Object): Packet object
                sender (str): sender's ip address
                
                Returns:
                None
                
                """
                if pkt.uuid in self.uuid_packet_cache:
                        return
                else:
                        print("new pkt from " +  pkt.ip + "\t\tuuid: " + pkt.uuid)
                        self.uuid_packet_cache.setdefault(pkt.uuid, None)

                if pkt.ip == sender and sender not in self.neighbors:
                        print("new neighbor discovery: " + sender)
                        self.neighbors.append(sender)
                        self.adj_table[self.ip].append(sender)

                if pkt.ip not in self.packet_table:
                        
                        self.packet_table.setdefault( pkt.ip, {})
        
                _uuid_table = self.packet_table[pkt.ip]
                _uuid_table.setdefault(pkt.uuid, pkt)


        def construct_topology(self, gpkt):
                """
                
                Constructs a topological tree from view to current node. The adjacency table
                constains the topological tree information. See Remarks below.
                
                
                Parameters:
                gpkt(GraphPacket):
                
                Returns:
                None
                
                
                Remarks:
                The adjacency table contains
                        Key-ip : neighbor1, neighbor2,..., neighborN
                
                Where each unique neighbor's ID, or ip, is kept. For each table, strip all
                non-unique ID's found in graph message. Create a new table with the remaining
                unique IDs and the table's name is the graph packets IP address.
                
                """

                if gpkt.uuid in self.uuid_packet_cache:
                        return False
                else:
                        self.uuid_packet_cache.setdefault( gpkt.uuid, None)

                _adj_list = gpkt.graph
                if self.ip in _adj_list:
                        _adj_list.remove(self.ip)

                for key_ip in _adj_list:
                        if key_ip in self.prev_neighbors:
                                _adj_list.remove(key_ip)

                self.adj_table.setdefault(gpkt.ip, _adj_list)

                return True

        def flush(self):

                """
                
                Flushes graph. Two graph adjacency tables are maintained--current and previous.

                Parameters:
                None

                Returns:
                None

                Remarks:
                Saves and clears adjacency list--used fro constructing the topological tree
                The packet table is also saved and cleared. All neighbors with an empty table are removed.
                """
                self.prev_neighbors = copy.deepcopy( self.neighbors)
                self.prev_packet_table = copy.deepcopy(self.packet_table)
                
                #clear if no packets in packet_table from Node with IP ip
                # then no longer a neighbor
                for neighbor in self.neighborse
                        if not self.packet_table[neighbor]:
                                self.neighbors.remove(neighbor)

                #clear all packets
                for key_ip in self.packet_table:
                        self.packet_table[key_ip] = {}

                #clear adj_list table for constructing tree (topology)
                self.adj_table.clear()
                self.adj_table.setdefault(self.ip, self.prev_neighbors)
                        
                for neighbor in self.prev_neighbors:
                        self.adj_table.setdefault(neighbor, None)
                


        #       
        # Remarks:
        #       -adj_list references self.prev_adj_list, this is a list containing IPs
        def to_json(self):
        """ Returns the previous adjacency list or list of previous neighbors"""
                return self.prev_neighbors


