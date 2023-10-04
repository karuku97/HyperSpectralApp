# This Python file uses the following encoding: utf-8
import sys

import functions

from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtQuickControls2 import *
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow
from secondwindows import *


class MainWindow(QMainWindow):
    """MainWindow"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # initalize Library Window
        self.current_TopLevelCount = 0
        self.libWin = LibraryWindow()

        # initialise MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Event connections
        # connect start Button to Funktion
        self.ui.btn_start.pressed.connect(self.start_btn_pressed)
        # connect delete Button to Funktion
        self.ui.btn_delete.pressed.connect(self.delete_btn_pressed)
        # connect connect Button to Funktion
        self.ui.btn_connect.pressed.connect(self.connectInputOutput)
        # connect LibraryBrowser Button to Funktion
        self.ui.btn_libraryBrowser.pressed.connect(self.libWin.show)
        # connect Main Tree clicked Event to Funktion
        self.ui.tree_main.clicked.connect(self.updateViewport)
        # add Eventfilter to Main Tree
        self.ui.tree_main.installEventFilter(self)

        # Show Ready Messge on Status Bar
        self.ui.statusbar.showMessage("Ready")

        # info Text
        self.info = (f'Instructions:\n'
                     f'\n1. choose functions from "Library Brwoser"\n'
                     f'2. drag and Drop them onto the "Run Diagram" (in right order)\n'
                     f'3. adjust all functions\n'
                     f'4. connect all functions\n'
                     f'    4.1 unfold all functions\n'
                     f'    4.2 select one input and one output to connect\n'
                     f'    4.3 connect them via "connect" button (green background if successful)\n'
                     f'5. run the Programm via "Start" button')

        self.ui.label.setToolTip( self.info)

        # instructions for first display
        self.showInstructions()

        self.ui.label.mousePressEvent = self.showInstructions

    def showErrorMassage(self, string: str):
        """sends Error Massage"""
        # print to Consol
        print(string)
        # Print to Statusbar
        self.ui.statusbar.showMessage(string)

    def showInstructions(self,e=None):
        """Mouse click call back funktion for showing Instructions """
        # delet current Frame
        wid = self.ui.gridLayout_2.itemAtPosition(0, 0)
        if wid != None: wid.widget().setParent(None)

        label = QLabel()
        label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.ui.gridLayout_2.setContentsMargins(10,10,10,10)
        self.ui.gridLayout_2.addWidget(label, 0, 0)
        label.setText(self.info)

    def updateViewport(self):
        """ Method to Update Viewport to selectet Funktion in Run Diagramm
        sets QFrame from selectet Funktion to display"""

        # get all selected Items on Main Tree
        items = self.ui.tree_main.selectedItems()
        # check if only one Item is selected and needs to be a Top Level Item
        if len(items) == 1:
            if items[0].parent() == None:

                # delet current Frame
                wid = self.ui.gridLayout_2.itemAtPosition(0, 0)
                if wid != None: wid.widget().setParent(None)

                # gets Frame from selected Funktion
                item = items[0].data(0, Qt.ItemDataRole.UserRole)
                wid = item.get_Viewport(self)
                # adds Frame to GridLayout
                self.ui.gridLayout_2.addWidget(wid, 0, 0)
                self.ui.gridLayout_2.setContentsMargins(0, 0, 0, 0)

    def connectInputOutput(self):
        """ connects One Input to an Output of the Funktion Diagram, Call by Button (connect)"""
        # gets all selected Items
        items = self.ui.tree_main.selectedItems()

        # checks if Items are two
        if len(items) == 2:
            # checks if selected items are named "Input" and "Output"
            if ((items[1].text(0) == "Input" and items[0].text(0) == "Output") or (
                    items[0].text(0) == "Input" and items[1].text(0) == "Output")):
                # sets the TreeItem as Data of the other Treeitem and vicevercer
                items[0].setData(0, Qt.ItemDataRole.UserRole, items[1])
                items[1].setData(0, Qt.ItemDataRole.UserRole, items[0])

                # checks if Data is set and modifys Backgroundcolor to green, if connection were made
                for item in items:
                    if item.data(0, Qt.ItemDataRole.UserRole) != None:
                        item.setBackground(0, Qt.green)
            # if wrong Items were selected.. show Error Massage
            else:
                self.showErrorMassage("Error: Selected items needs to be nemed 'Input' and 'Output")
        # if not exactly two Items were selected.. show an Error Massage
        else:
            self.showErrorMassage("Error: not exactly two Items were selected")

    def eventFilter(self, o, e) -> bool:
        """ EventFilter to call Update View, to add Input and Ouput Ports to Function in Run Diagram"""
        # checks if Event comes rom Main Tree and Toplevel count has changed
        if o == self.ui.tree_main and self.current_TopLevelCount != self.ui.tree_main.topLevelItemCount():
            # calls update Funktion
            self.updateView()
            # sets current TopLevel Count
            self.current_TopLevelCount = self.ui.tree_main.topLevelItemCount()
        return True

    def updateView(self):
        """ Updates Run Diagramm, is called by EventFilter. Adds Input and Output Points"""
        # loops throuh every TopLevel Item in Main Tree
        for i in range(self.ui.tree_main.topLevelItemCount()):
            item = self.ui.tree_main.topLevelItem(i)
            data = item.data(0, Qt.ItemDataRole.UserRole)
            # checks if current child count is not equal to supposed Input/Output count
            if item.childCount() != data.output_count + data.input_count:
                # takes all current children
                for j in range(item.childCount()):
                    item.takeChildren()
                # adds Inputs as Children
                for i in range(data.input_count):
                    child = QTreeWidgetItem()
                    child.setText(0, "Input")
                    item.addChild(child)
                # adds Outputs as Children
                for z in range(data.output_count):
                    child = QTreeWidgetItem()
                    child.setText(0, "Output")
                    # child.setData(0, Qt.ItemDataRole.UserRole, data.input_point)
                    item.addChild(child)
            # loops throu every Child
            for j in range(item.childCount()):
                child = item.child(j)
                # checks if child has no Data and sets Backgroundcolor to red + takes all children of the child
                if child.data(0, Qt.ItemDataRole.UserRole) == None:
                    child.setBackground(0, Qt.red)
                    child.takeChildren()

    def start_btn_pressed(self):
        """Called by Start Button, Runs the Run Diagramm from Top to bottom and sets all predefined OutPut Input
        connections"""

        # checks if Funktions are in the main Tree
        if self.ui.tree_main.topLevelItemCount() == 0:
            self.showErrorMassage("Error: No actions provided")
            return False

        # loops throu Main Tree Items from top to bottom
        for i in range(self.ui.tree_main.topLevelItemCount()):
            first = self.ui.tree_main.topLevelItem(i)
            data = first.data(0, Qt.ItemDataRole.UserRole)

            # chekcks if more than 1 Funktions are provided
            if i > 0:
                # gets connected Input ( First Child )
                connected_input = first.child(0).data(0, Qt.ItemDataRole.UserRole)
                # checks if Input Element were provided els shows Error Massage
                if connected_input == None:
                    self.showErrorMassage("Error: Missing Connection!")
                    return False
                # sets input data to output data of
                dataa = connected_input.parent().data(0, Qt.ItemDataRole.UserRole)
                data.input_value = dataa.output_value
            # runs Funktion
            rtn = data.run()
            # checks if Funktion were run succsessfully
            if rtn != True:
                self.showErrorMassage("Error: in Fuction")
                return False

        # prints Success Message
        self.showErrorMassage("Run successfully")
        # updates Viewport
        self.updateViewport()

    def delete_btn_pressed(self):
        """Delets selected functions in Run Diagram, call at Button Press (delete)"""
        tree = self.ui.tree_main
        root = tree.invisibleRootItem()
        # loops throu selected itmes and their children of Main Tree
        for item in tree.selectedItems():
            for i in range(item.childCount()):
                child = item.child(i)
                # gets connected Input and Output Items
                connected = child.data(0, Qt.ItemDataRole.UserRole)
                if (connected != None):
                    # sets Input and Output elements to None
                    connected.setData(0, Qt.ItemDataRole.UserRole, None)
            # removes items
            (item.parent() or root).removeChild(item)
        # updates Tree View
        self.updateView()

    def closeEvent(self, e):
        """Close Event, for MainWindow"""
        QApplication.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
