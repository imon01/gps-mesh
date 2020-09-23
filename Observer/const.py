def enum(**enums):
	return type('Enum', (), enums)

INTERVAL = enum( FULL="full", CURR="current", INTVL="interval", TIME="time")

SERVICE = enum( DATA="data", NETSTAT="net_stat", GPSSTAT="gps_stat")
