# This Python file uses the following encoding: utf-8
import sys

import functions

from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidget, QTreeWidgetItem, QGraphicsRectItem, QGraphicsItem, \
    QGraphicsTextItem, QGraphicsSceneMouseEvent, QGraphicsLineItem
from PySide6.QtGui import *
from PySide6.QtCore import *
from PySide6.QtQuickControls2 import *
# Important:
# You need to run the following command to generate the ui_form.py file
#     pyside6-uic form.ui -o ui_form.py, or
#     pyside2-uic form.ui -o ui_form.py
from ui_form import Ui_MainWindow
from secondwindows import *

class DraggableRectItemBlock(QGraphicsRectItem):
    def __init__(self, rect, index, main_window, parent=None):
        super().__init__(rect, parent)
        self.main_window = main_window
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setBrush(QBrush(Qt.lightGray))
        self.index = index
        self.original_position = None
        self.TextItem = QGraphicsTextItem("Text", self)
        self.rect_height = 200
        self.rect_width = 50

    def mousePressEvent(self, event: QMouseEvent):
        self.original_position = self.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.main_window.updateItemPosition(self, self.index)
        super().mouseReleaseEvent(event)


class DraggableRectItemConnector(QGraphicsRectItem):
    def __init__(self, rect, main_window, parent):
        super().__init__(rect, parent)
        self.setParentItem(parent)
        self.setFlags(QGraphicsItem.ItemIsSelectable )
        self.setBrush(QBrush(Qt.lightGray))
        self.main_window = main_window
        self.connectedTo = []
        self.rect_height = 10
        self.rect_width = 10

        self.original_position = None

    def mousePressEvent(self, event: QMouseEvent):
        self.original_position = self.pos()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.main_window.connectConnectors(self,event)
        super().mouseReleaseEvent(event)

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


        # # Show Ready Messge on Status Bar
        self.ui.statusbar.showMessage("Ready")
        #
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

        self.blocks = []
        self.create_blocks(5)


    def showErrorMassage(self, string: str):

        """sends Error Massage"""
        # print to Consol
        print(string)
        # Print to Statusbar
        self.ui.statusbar.showMessage(string)

    def showInstructions(self,e=None):
        pass
        """Mouse click call back funktion for showing Instructions """
        # delet current Frame
        wid = self.ui.gridLayout_2.itemAtPosition(0, 0)
        if wid != None: wid.widget().setParent(None)

        label = QLabel()
        label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        self.ui.gridLayout_2.setContentsMargins(10,10,10,10)
        self.ui.gridLayout_2.addWidget(label, 0, 0)
        label.setText(self.info)

    def create_blocks(self, count):
        rect_height = 50
        rect_width = 200

        for i in range(count):
            y_offset = i * (rect_height + 10)
            rect = DraggableRectItemBlock(QRectF(0, 0, rect_width, rect_height), i, self)
            rect.setPos(0,y_offset)
            rect.rect_height = rect_height
            rect.rect_width = rect_width

            rect.TextItem.setPos(10, 10)
            rect.TextItem.setPlainText(f'Block {i}')

            input = DraggableRectItemConnector(QRectF(rect_width,(rect_height/2)-5,10,10),self,rect)


            self.ui.scene.addItem(rect)
            self.blocks.append(rect)


    def updateItemPosition(self, moved_item, moved_index):
        #print(moved_item.TextItem.toPlainText())
        rect_height = 50
        new_index = round(moved_item.y() / (rect_height + 10))
        new_index = max(0, min(new_index, len(self.blocks) - 1))

        # Entfernen des verschobenen Blocks aus seiner alten Position
        if new_index != moved_index:
            self.blocks.pop(moved_index)
            # Einfügen des verschobenen Blocks an der neuen Position
            self.blocks.insert(new_index, moved_item)

        # Aktualisieren der Positionen aller Blöcke
        for i, block in enumerate(self.blocks):
            block.index = i
            target_y = i * (rect_height + 10)
            if block.y() != target_y:
                block.setPos(QPointF(0, target_y))

        self.updateAllConnections()

    def connectConnectors(self, moved_connecor: DraggableRectItemConnector, event: QGraphicsSceneMouseEvent):
        itemAtClick = moved_connecor
        # print(moved_connecor.parentItem().TextItem.toPlainText())
        # print(event)
        itemAtRelease = self.ui.scene.itemAt(event.scenePos().x(), event.scenePos().y(), self.ui.gph_view.transform())
        print(itemAtRelease.parentItem().TextItem.toPlainText())
        print(itemAtRelease.scenePos())
        if isinstance(itemAtRelease, DraggableRectItemConnector):
            itemAtClick.connectedTo.append(itemAtRelease)
            itemAtRelease.connectedTo.append(itemAtClick)

            # offset berechnen
            offset = 10
            i = itemAtRelease.parentItem().index + itemAtClick.parentItem().index

            # Vertikale linie
            x1 = itemAtClick.rect().x() + 5 + (i * offset)
            y1 = itemAtClick.rect().y() + 5
            x2 = itemAtRelease.parentItem().rect().x() + itemAtRelease.parentItem().rect_width + itemAtRelease.rect_width / 2 + (
                        i * offset)
            y2 = itemAtRelease.parentItem().y() + itemAtRelease.parentItem().rect_height / 2 - itemAtClick.parentItem().y()
            line = QGraphicsLineItem(x1, y1, x2, y2, moved_connecor)

            # Horrizontale linie

            line = QGraphicsLineItem(x1 - (i * offset), y1, x1, y1, moved_connecor)
            line = QGraphicsLineItem(x2 - (i * offset), y2, x2, y2, moved_connecor)

            # self.scene.addItem(line)
            print("connect")
        print("Draged")

    def updateAllConnections(self):
        for b in self.blocks:
            #b = DraggableRectItemBlock
            for b_c in b.childItems():
                if(isinstance(b_c,DraggableRectItemConnector)):
                    #print(b_c)
                    con_from = b_c

                    for con_to in b_c.connectedTo:
                        #print(con_to)
                        if con_to is not None :

                            for child in b_c.childItems():
                                #print(child)
                                self.ui.scene.removeItem(child)
                                del child



                            # offset berechnen
                            offset = 10
                            i = con_to.parentItem().index + con_from.parentItem().index

                            # Vertikale linie
                            x1 = con_from.rect().x() + 5 + (i * offset)
                            y1 = con_from.rect().y() + 5
                            x2 = con_to.parentItem().rect().x() + con_to.parentItem().rect_width + con_to.rect_width / 2 + (
                                        i * offset)
                            y2 = con_to.parentItem().y() + con_to.parentItem().rect_height / 2 - con_from.parentItem().y()
                            line1 = QGraphicsLineItem(x1, y1, x2, y2, con_from)

                            # Horrizontale linie

                            line2 = QGraphicsLineItem(x1 - (i * offset), y1, x1, y1, con_from)
                            line3 = QGraphicsLineItem(x2 - (i * offset), y2, x2, y2, con_from)


    def updateViewport(self):
        pass


    def connectInputOutput(self):
        pass


    def eventFilter(self, o, e) -> bool:
        pass


    def updateView(self):
        pass


    def start_btn_pressed(self):
        pass


    def delete_btn_pressed(self):

        pass

    def closeEvent(self, e):
        """Close Event, for MainWindow"""
        QApplication.exit()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MainWindow()
    widget.show()
    sys.exit(app.exec())
