import time
import socket
import select
import traceback, sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from gui import Ui_MainWindow
from models import *
from Node import *
from datetime import *
from subprocess import Popen
import pymongo
from pymongo import *
#<<<<<<< HEAD
from display import *
import pickle
import pprint
import json
#=======


#>>>>>>> develop
import select
import socket

nodeList = []
gpsCoords = dict()

def recvall(s):
    '''
    recvall is a function which will be used to receive the full data sent over from nodes
    when sending the log data to the observer.  It blocks until the whole packet is received
    to assure the complete log is intact.
    '''
    BUFF = 1024
    data = b''
    while True:
        portion = s.recv(BUFF, socket.MSG_WAITALL)
        data += portion
        if len(portion) < BUFF:
            break
    return data

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)
    collected = pyqtSignal(object)

class Worker(QRunnable):
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()


        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        kwargs['collected'] = self.signals.collected

        # Add the callback to our kwargs
        # kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done



class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #buttonSetup(self.ui)
        #self.createTable()
        #self.show()
        self.buttonSetup(self.ui)
        #gui.createObjects()
        self.createObjects()
        self.show()
        self.displayGPSdata("EXAMPLE", "192.168.2.2", "10/10/10", "1231.32", "546.22")
        self.displayGPSdata("EXAMPLE", "192.168.2.2", "11/11/11", "1255.32", "9999.22")
        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())
        self.node = Node(8000)


    def createObjects(self):
        self.displayButtonSetup()

    def displayButtonSetup(self):
        self.ui.clearButton.clicked.connect(self.clearTable)
        self.ui.clearButton2.clicked.connect(self.clearTable2)
        #self.ui.testButton9.clicked.connect(self.testButton9)
        self.ui.ListenLoopButton.clicked.connect(self.udpThread)
        self.ui.retrieveLogButton.clicked.connect(self.retrieve_logs)
        self.ui.tcpButton.clicked.connect(self.tcpThread)

    def clearTable(self):
        self.ui.tableWidget_2.setRowCount(0)

    def clearTable2(self):
        self.ui.tableWidget.setRowCount(0)
        clearNodeList()


    '''def testButton9(self):
        print (str(nodeList))'''

    def getUI(self):
        return self.ui

    def displayGPSdata(self, name, address, timeStamp, longitude, latitude):
        table = self.ui.tableWidget_2
        rowPosition = table.rowCount()
        table.insertRow(rowPosition)
        table.setItem(rowPosition , 0, QTableWidgetItem(name))
        table.setItem(rowPosition , 1, QTableWidgetItem(address))
        table.setItem(rowPosition , 2, QTableWidgetItem(timeStamp))
        table.setItem(rowPosition , 3, QTableWidgetItem(longitude))
        table.setItem(rowPosition , 4, QTableWidgetItem(latitude))
        self.displayNodeList(name, address)

    def displayNodeList(self, name, address):
        if address not in nodeList:
            table = self.ui.tableWidget
            rowPosition = table.rowCount()
            table.insertRow(rowPosition)
            table.setItem(rowPosition , 0, QTableWidgetItem(name))
            table.setItem(rowPosition , 1, QTableWidgetItem(address))
            nodeList.append(address)

    def clearNodeList():
        nodeList.clear()

    def buttonSetup(self, ui):
        print("")
        #ui.ListenLoopButton.clicked.connect(listen_loop())
        #ui.testButton1.clicked.connect(self.testFunction1)
        #ui.testButton2.clicked.connect(self.testFunction2)
        #ui.testButton3.clicked.connect(self.testFunction3)
        #ui.testButton4.clicked.connect(self.testFunction4)
        #ui.testButton5.clicked.connect(self.testFunction5)
        #ui.testButton6.clicked.connect(self.testFunction6)
        #ui.testButton6.clicked.connect(listen_loop())
        #Set up for Clear Button
        #app.clearButton.clicked.connect(clearGPSdata(app))

    def test_loop(self, collected):
        for n in range(0, 5):
            collected.emit(("TEST!","10.10.1.1", "10/10/10", 1231.32, 546.22))
            #time.time.sleep(1)

    def retrieve_logs(self):
        queryPkt = QueryPacket("0.0.0.0", "0", SERVICE.DATA, INTERVAL.FULL)
        self.node.send(queryPkt)
        print("sent queryPkt")
        
        # Write TCP listening loop below
        #listen_tcp()


    
    def listen_tcp(self, collected):
        ''' 
        listen_tcp is a loop which waits for tcp connections from the nodes.
        Once a node is connected and the retrieve logs button is pressed on the 
        observer gui, a signal is sent to all nodes to dump their logs.
        Once a connection is received the logs are sent in a json binary form to
        the observer.  The json is decoded as a dict. The entries in data are in the form:
        timestamp|node IP|packet type|uuid|{packet type specific data}
        
        For each entry split on "|" and create an entry to be added to the database 
        using the accompanying fields.  Currently only gps packets are taken from the log
        and added to the database.        
        '''
        port = 10000
        cmax = 50#nodeListCount()
        sd = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sd.bind(("10.0.0.3", port))
        sd.listen(cmax)
        print("start tcp listen loop")
        read_list = [sd]
        while True:
            r, w, e = select.select(read_list, [], [])
            for listen in r:
                if listen is sd:
                    conn, addr = sd.accept()
                    print("got connection")
                    data = recvall(conn)
                    ndata = json.loads(data.decode())
                    print("data type ", type(ndata))
                    for i in ndata["data"]:
                        pktdat = i.split("|")
                        if pktdat[2] == "gps":
                            if(db.find({"uuid" : pktdat[3]}).count() == 0):
                                track = {"ip":pktdat[1], "time":pktdat[0], "uuid" : pktdat[3], "lat":pktdat[4], "lng":pktdat[5]}
                                pprint.pprint(track)
                                track_id = db.insert_one(track).inserted_id
                    conn.close()
                    



    def collectedSignalFunction(self, tup):
        name = tup[0]
        address = tup[1]
        timestamp = tup[2]
        longitude = tup[3]
        latitude = tup[4]
        self.displayGPSdata(str(name), str(address), str(timestamp), str(longitude), str(latitude))

    def udpThread(self):
        '''
        udpThread creates a thread for monitoring the udp traffic over the network
        and add it to the threadpool.
        '''
        worker = Worker(self.listen_loop)
        #worker = Worker(self.test_loop)
        worker.signals.collected.connect(self.collectedSignalFunction)
        self.threadpool.start(worker)

    def tcpThread(self):
        '''
        tcpThread creates a thread for monitoring the tcp traffic over the network
        and add it to the threadpool.
        '''
        tcp_Worker = Worker(self.listen_tcp)
        #worker = Worker(self.test_loop)
        #worker.signals.collected.connect(self.collectedSignalFunction)
        self.threadpool.start(tcp_Worker)

    ##################################################################

    def displayGUI():
        #app = QApplication(sys.argv)
        #gui = AppWindow()
        buttonSetup(self.ui)
        #gui.createObjects()
        self.ui.creatObjects()
        gui.show()
        displayGPSdata(gui, "EXAMPLE", "192.168.2.2", "10/10/10", "1231.32", "546.22")
        displayGPSdata(gui, "EXAMPLE", "192.168.2.2", "11/11/11", "1255.32", "9999.22")
        sys.exit(app.exec_())
        #
        return gui

    ##################################################################


    '''def testFunction1(self):
            print("test 1: Hello World!")  # replace print statement with a function call :)

    def testFunction2(self):
            print("test 2: Hello World!")

    def testFunction3(self):
            print("test 3: Hello World!")

    def testFunction4(self):
            print("test 4: Hello World!")

    def testFunction4(self):
            print("test 4: Hello World!")
            self.node.node_close()

    def testFunction5(self):
            print("test 5: Hello World!")

    def testFunction6(self):
            listen_loop()'''

	#TODO
					


    def listen_loop(self, collected):
            ''' 
            listen_loop is a loop which runs constantly on its own thread.
            It's purpose is to listen for udp packets which are broadcast across the mesh.
            Once a packet is received, decode its entries and then save them in the database.
            
            The database entries are as follows:
            {"ip":nodeip, "time":time, "uuid" : uuid, "lat":lat, "lng":lng}
            
            Currently only gps packets are saved in the database.
            '''
            print("in listen loop")
            n = self.node
            while True:
                    #print("in while loop")
                    try:
                            readers = select.select([sys.stdin.fileno(), n.server], [], [])[0]
                            for reader in readers:
                                    if reader == n.server:
                                            addr, pkt = n.recv()
                                            if pkt is not None:
                                                    #save stuff to list
                                                    if pkt.pkt_type == "gps":
                                                            ip = str(pkt.ip)
                                                            time = str(pkt.timestamp)
                                                            uuid = str(pkt.uuid)
                                                            lng = str(pkt.lng)
                                                            lat = str(pkt.lat)
                                                            
                                                            print("ip: " + ip + ", time " + time + ", lat " + lat + ", lng " + lng +", uuid " + uuid)
                                                            if pkt.ip not in gpsCoords:
                                                                    gpsCoords[pkt.ip]= {}
                                                            gpsCoords[ip][time] = [lng + ", " + lat]						
                                                            #print("lat", str(lat)," lon", str(lng))
                                                            ## If the uuid is not found in any entry in db, add it to the db.
                                                            if(db.find({"uuid" : uuid}).count() == 0):
                                                                    track = {"ip":ip, "time":time, "uuid" : uuid, "lat":lat, "lng":lng}
                                                                    track_id = db.insert_one(track).inserted_id
                                                            #displayGPSdata(gui, str(pkt.ip), str(pkt.ip), str(pkt.timestamp), str(pkt.lng), str(pkt.lat))
                                                            collected.emit((ip, ip, time, lng, lat)) # <----Tuple that returns collected values
                                                    #save stuff to db
                                                    pkt.ttl -= 1
                                                    if pkt.ttl > 0:
                                                            n.send(pkt)
                                                    pkt = None
                    except IOError as e:
                            print("something went wrong")

def init_wifi():
        '''
        init_wifi will run a script which sets up the machines wireless network card
        to run in ad-hoc mode. Inside the script itself the wireless adapter name will
        likely need to be changed when running on other machines.
        '''
        #os.system("./reset_wi.sh")
        os.system("./set_adhoc.sh")


'''
Start of the program.
Initializes wifi card to ad-hoc mode.
Opens the mongoDB host. Connect to the host.
Set up database and collection.  
##This is still in progress as it is not using the string saved in dbname, but instead 
##using the variable name 'dbname'
Finally initialize the gui and window, then start executing the threads.
'''
init_wifi()
## start mongoDB host
pid = Popen("mongod", shell=True).pid
## start mongoDB client
client = MongoClient('localhost', 27017)
'''
The following 6 lines create and start the database, will become fully initialized when the
first entry is added to db in listen_loop
'''
now = datetime.now()
today = str(now.year) + "/" + str(now.month) + "/" + str(now.day) + "_" + str(now.hour) + ":" + str(now.minute)
racename = "BoatRace_"
dbname = racename + today
race = client.dbname
db = race.race

app = QApplication([])
window = AppWindow()
app.exec_()

#print(client.database_names())

#listen_loop()
