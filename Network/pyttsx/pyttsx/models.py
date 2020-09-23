import json
import uuid
import copy
import socket
import datetime

class BasePacket( object) :
	def __init__(self):
		self.ip = socket.gethostbyname( socket.gethostname() )
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





#------------------------------------------------------
class Graph:
	def __init__(self, ip):

		self.ip = ip
		self.adj_list = {ip: {}}
		self.prev_adjlist = {ip:{}}
		self.ip_cache = list()
		self.ip_cache.append(ip)


	def add_vertex(self, v):
		self.adj_list.setdefault(v, [])

	def add_edge(self, v, e):
		try:
			self.adj_list[v].append(e)
		except:
			raise Exception("Vertex {} not found in graph".format(v))
	
	#
	#
	#	
	def store(self, pkt):
		print( "store: self.ip --> " + self.ip )
		self.adj_list[self.ip].setdefault( pkt.uuid, pkt)


	# Table lookpup with <IP>
	# 
	#
	#   Remarks:
	#   -table is a list of neighboring nodes IP one-hop away
	#   -pkt.ip is origin ip of packet's sender
	#
	def filter(self, pkt):
		if pkt.ip == self.ip:
			return

		if pkt.ip not in self.ip_cache:
			print("new ip cached")
			self.ip_cache.append( pkt.ip )	

		if pkt.ip not in self.adj_list:
			print( "new neigbor discovery ")
			self.add_vertex(pkt.ip)

		self.uuid_table( pkt )



	#
	#	uid_table format :  {key = pkt uuid, value = gps packet}
	#
	#	Remarks:
	#	-table is hashed by using packet originating IP address
	#
	#
	#
	def uuid_table( self, pkt ):

		if pkt.ip not in self.adj_list:
			return 

		uid_table = self.adj_list[pkt.ip]

		# if pkt cannot be mapped in uid_table, then it hasn't been observed
		if pkt.uuid not in uid_table:
			print( "new pck from neighbor: " + pkt.ip )
			uid_table.setdefault( pkt.uuid, pkt )

	#
	#   Remarks:
	#   -Network topology constructed from bcast graph and inserted  into 
	#      previous adjancy list 
	#
	def construct_topology(self, bcast_graph):
		if not isinstance( bcast_graph, dict):
			print( "construct_topology requires dictionary")
			return

		prev_graph = self.prev_adjlist

		# Prune self.ip from Graph broadcast
		if self.ip in bcast_graph:
			prev_graph.pop(self.ip, None)

		#
		# Anchor associated adj list (table) of ip into prev_graph
		for ip_key in bcast_graph:

			if ip_key in prev_graph:
				prev_graph[ip_key] = bcast_graph[ip_key]

	#
	# Remarks:
	# -if the associatied uuid_table for some node with IP ip empty
	#   then node packets received from that node and not a neighbor
	#
	# -self.ip removed for redundant check
	def flush(self):
		_ip_table = self.adj_list
		self.prev_adjlist = copy.deepcopy(self.adj_list)
		print(10*"______"+"\n\n pre flush")

		_ip_table.pop( self.ip, None)
		for ip in self.ip_cache:
			if ip in _ip_table and not _ip_table[ip]:
				_ip_table.pop(ip, None)

			if ip in _ip_table:
				_ip_table[ip] = {}

		_ip_table.setdefault( self.ip, {} ) 

		print("\npot flush\n" + 10*"_____" + "\n\n")



	def prettyprint( self, graph_opt):
		print("\n\n pretty print.... \n\n")

		_ip_table = self.adj_list

		if not graph_opt:
			_ip_table = self.prev_adjlist

		for ip in _ip_table:
			print("IP: " + ip + " uuid table")
			_uuid_table = _ip_table[ip]

			for key_uuid in _uuid_table:
				print( "t\t"+ str(key_uuid) + _uuid_table[key_uuid].timestamp)

		print(10*"------"+"\n\n")



	def to_json(self):
		return self.adj_list

