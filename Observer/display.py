import sys
from PyQt5.QtWidgets import QDialog, QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from gui import Ui_MainWindow


nodeList = []


class AppWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        #buttonSetup(self.ui)
        #self.createTable()
        #self.show()


    def createObjects(self):
        self.displayButtonSetup()


    '''def createTable(self):
        self.ui.tableWidget_2.setRowCount(10)
        self.ui.tableWidget_2.setColumnCount(10)
        self.ui.tableWidget_2.setItem(0,0, QTableWidgetItem("Cell (1,1)"))
        self.ui.tableWidget_2.setItem(0,1, QTableWidgetItem("Cell (1,2)"))
        self.ui.tableWidget_2.setItem(1,0, QTableWidgetItem("Cell (2,1)"))
        self.ui.tableWidget_2.setItem(1,1, QTableWidgetItem("Cell (2,2)"))
        self.ui.tableWidget_2.setItem(2,0, QTableWidgetItem("Cell (3,1)"))
        self.ui.tableWidget_2.setItem(2,1, QTableWidgetItem("Cell (3,2)"))
        self.ui.tableWidget_2.setItem(3,0, QTableWidgetItem("Cell (4,1)"))
        self.ui.tableWidget_2.setItem(3,1, QTableWidgetItem("Cell (4,2)"))

        self.ui.tableWidget.setRowCount(10)
        self.ui.tableWidget.setColumnCount(10)
        self.ui.tableWidget.setItem(0,0, QTableWidgetItem("Cell (1,1)"))
        self.ui.tableWidget.setItem(0,1, QTableWidgetItem("Cell (1,2)"))
        self.ui.tableWidget.setItem(1,0, QTableWidgetItem("Cell (2,1)"))
        self.ui.tableWidget.setItem(1,1, QTableWidgetItem("Cell (2,2)"))
        self.ui.tableWidget.setItem(2,0, QTableWidgetItem("Cell (3,1)"))
        self.ui.tableWidget.setItem(2,1, QTableWidgetItem("Cell (3,2)"))
        self.ui.tableWidget.setItem(3,0, QTableWidgetItem("Cell (4,1)"))
        self.ui.tableWidget.setItem(3,1, QTableWidgetItem("Cell (4,2)"))'''

    def displayButtonSetup(self):
        self.ui.clearButton.clicked.connect(self.clearTable)
        self.ui.clearButton2.clicked.connect(self.clearTable2)
        #self.ui.testButton9.clicked.connect(self.testButton9)

    def clearTable(self):
        self.ui.tableWidget_2.setRowCount(0)

    def clearTable2(self):
        self.ui.tableWidget.setRowCount(0)
        clearNodeList()


    '''def testButton9(self):
        print (str(nodeList))'''

    def getUI(self):
        return self.ui

def displayGPSdata(gui, name, address, timeStamp, longitude, latitude):
    table = gui.ui.tableWidget_2
    rowPosition = table.rowCount()
    table.insertRow(rowPosition)
    table.setItem(rowPosition , 0, QTableWidgetItem(name))
    table.setItem(rowPosition , 1, QTableWidgetItem(address))
    table.setItem(rowPosition , 2, QTableWidgetItem(timeStamp))
    table.setItem(rowPosition , 3, QTableWidgetItem(longitude))
    table.setItem(rowPosition , 4, QTableWidgetItem(latitude))
    displayNodeList(gui, name, address)

def displayNodeList(gui, name, address):
    if address not in nodeList:
        table = gui.ui.tableWidget
        rowPosition = table.rowCount()
        table.insertRow(rowPosition)
        table.setItem(rowPosition , 0, QTableWidgetItem(name))
        table.setItem(rowPosition , 1, QTableWidgetItem(address))
        nodeList.append(address)

def clearNodeList():
    nodeList.clear()

def nodeListCount():
    return len(nodeList)