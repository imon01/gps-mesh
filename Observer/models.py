import json
import uuid
import copy
import socket
import datetime
from const import *

class BasePacket( object) :
	def __init__(self):
		self.ip = "10.0.0.3"#socket.gethostbyname( socket.gethostname() )
		self.ttl = 30
		self.uuid = str(uuid.uuid1())
		self.timestamp = str(datetime.datetime.now())

	def to_json(self):
		return {"ip": self.ip,"ttl":self.ttl, "uuid": self.uuid, "timestamp": self.timestamp}

class GPSPacket(BasePacket):
	def __init__(self, lat, lng, json_pkt=None):
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
		packet_json = super(GPSPacket, self).to_json()
		packet_json['lat'] = self.lat
		packet_json['lng'] = self.lng
		packet_json["pkt_type"] = self.pkt_type
		return packet_json

class GraphPacket(BasePacket):
	def __init__(self, graph, json_pkt=None):
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
		packet_json = super(GraphPacket, self).to_json()
		packet_json['graph'] = self.graph
		packet_json['pkt_type'] = self.pkt_type
		return packet_json

class MessagePacket(BasePacket):
	def __init__(self, message, json_pkt=None):
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
		packet_json = super(MessagePacket, self).to_json()
		packet_json['message'] = self.message
		packet_json["pkt_type"] = self.pkt_type
		return packet_json

class QueryPacket(BasePacket):
	def __init__(self, dst_ip, query_id, service, interval=None, json_pkt=None, time=None, delta=None):
		
		
		if json_pkt is None:
			self.dst_ip	= dst_ip 
			self.query_id	= query_id
			self.pkt_type	= "query"
			self.service	= service
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
			self.ip		= json_pkt['ip'] 
			self.ttl	= json_pkt['ttl']
			self.uuid	= json_pkt['uuid']
			self.time	= json_pkt['time']
			self.delta	= json_pkt['delta']
			self.dst_ip	= json_pkt['dst_ip']
			self.service	= json_pkt['service']
			self.interval 	= json_pkt['interval']
			self.pkt_type	= json_pkt['pkt_type']
			self.query_id	= json_pkt['query_id']
			self.timestamp	= json_pkt["timestamp"]

	def to_json(self):
		packet_json		= super(QueryPacket, self).to_json()
		packet_json['time']	= self.time
		packet_json['delta']	= self.delta
		packet_json['dst_ip']	= self.dst_ip
		packet_json['service']	= self.service
		packet_json['interval']	= self.interval
		packet_json['query_id']	= self.query_id
		packet_json["pkt_type"] = self.pkt_type
		return packet_json


#Acknowledgment packet for query packet
class AckPacket(BasePacket):
	
	def __init__(self, dst_ip, query_id, service, data=None, json_pkt=None):
		if json_pkt is None:
			self.dst_ip	= dst_ip
			self.query_id	= query_id
			self.pkt_type 	= "ack"

			if service is SERVICE.DATA:
				try:
					self.data = data
				except:
					raise Exception("must provide data for Serivce data request")
			
			super(AckPacket, self).__init__()

		else:
			self.ip		= json_pkt['ip']
			self.ttl	= json_pkt['ttl']
			self.uuid	= json_pkt['uuid']
			self.data	= json_pkt['data']
			self.dst_ip	= json_pkt['dst_up']
			self.query_id	= json_pkt['query_id']
			self.pkt_type	= json_pkt['pkt_type']
			self.timestamp	= json_pkt['timestamp']

	def to_json(self):
		packet_json	= super(AckPacket, self).to_json()
		packet_json['time']	= self.time
		packet_json['delta']	= self.delta
		packet_json['dst_ip']	= self.dst.dst_ip
		packet_json['service']	= self.service
		packet_json['interval']	= self.interval
		packet_json['query_id']	= self.query_id
		packet_json['pkt_type']	= self.pkt_type
		return packet_json
#------------------------------------------------------
# 
#
# Remarks:
#	-adjancy list is contains imediate neighbors
class Graph:
	def __init__(self, ip):
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
	#	-Store self packets
	#	
	def store(self, pkt):
		print( "store: self.ip --> " + self.ip + "\t\t uuid: " + str(pkt.uuid ) )
		self.uuid_packet_cache.setdefault( pkt.uuid, None)
		_uuid_table = self.packet_table[self.ip]
		_uuid_table.setdefault(pkt.uuid, pkt)


	# 
	# Remarks:
	#	-filter packets by looking at packet's uuid, store if new
	#
	def filter(self, pkt, sender):
		#if pkt.ip == self.ip:
		#	return

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
	
	#
	# Remarks:
	#	-constructs topological tree from view of Node with IP ip (self.ip)
	#
	def construct_topology(self, gpkt):


		#filter graph packets, dont store if haven't seen	
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
	
	#
	# Remarks:
	#	-Saves and clears adjacency list. Saved adjacency list used for walking through adjacency table
	#	-Saves and clear packet table, saved to self.prev_packet_table.
	#		This table is used for constructing the topological tree
	#	-Removes nodes from neighboring adjacency list if packet table for that node is empty
	#
	def flush(self):
		print("graph flush")		
		self.prev_neighbors = copy.deepcopy( self.neighbors)
		self.prev_packet_table = copy.deepcopy(self.packet_table)
		
		#clear if no packets in packet_table from Node with IP ip
		# then no longer a neighbor
		for neighbor in self.neighbors:
			if not self.packet_table[neighbor]:
				self.neighbors.remove(neighbor) 

		#clear all packets
		for key_ip in self.packet_table:
			self.packet_table[key_ip] = {}

		#clear adj_list table for constructing tree (topology)
		self.adj_table.clear()
		self.adj_table.setdefault(self.ip, self.prev_neighbors)
	
			
		for neighbor in self.prev_neighbors:
			self.adj_table.setdefault(neighbor, )
		
		print("table adj: " + str( self.adj_table))

	#walk through previous table if
	def prettyprint(self, graph_opt):
		
		if not graph_opt is None:
			return
		
		_graph = self.neighbors
		_packet_table = self.packet_table
		if graph_opt:
			print("graph is previous graph\n\n")
			_graph = self.prev_neighbors
			_packet_tabl = self.prev_packet_table
		#TODO rebuild print 

	#	
	# Remarks:
	#	-adj_list references self.prev_adj_list, this is a list containing IPs
	def to_json(self):        
		return self.prev_neighbors

	
