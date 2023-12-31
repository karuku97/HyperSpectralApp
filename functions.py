from abc import ABC, abstractmethod

from PySide6 import QtGui, QtCore
from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QHeaderView,
                               QMainWindow, QMenuBar, QPushButton, QSizePolicy,
                               QStatusBar, QTreeWidget, QTreeWidgetItem, QWidget, QLabel, QLineEdit, QFrame, QTextEdit,
                               QFileDialog, QSlider, QSpacerItem, QScrollArea, QTextBrowser)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvasQTAgg
import matplotlib.pyplot as plt

from spectral import envi
import spectral as sp
import cv2.cv2 as cv
from PIL import Image
from PIL.ImageQt import ImageQt
import numpy as np
import bisect
import matplotlib.pyplot as plt
import random
import csv


class function(ABC):
    """ Interface function"""

    def __init__(self):
        """ initialisation"""
        # Input count, Point (TreeWidget) and Value
        self.input_count = 0
        self.input_point = None
        self.input_value = None
        # Output count, Point (TreeWidget) and Value
        self.output_count = 0
        self.output_point = None
        self.output_value = None
        # function name
        self.name = ""
        self.Debug = False
        self.info = "ToolTip"

    def __del__(self):
        """destructor"""
        print(f'{self.name} deleted.')

    @abstractmethod
    def run(self):
        """run function, provides calculation"""
        pass

    def createTreeWidget(self) -> QTreeWidgetItem:
        """returns Tree Widet to display in Library Window"""
        newTreeItem = QTreeWidgetItem()
        newTreeItem.setText(0, self.name)
        newTreeItem.setData(0, Qt.ItemDataRole.UserRole, self)
        newTreeItem.setToolTip(0, self.info)
        return newTreeItem

    @abstractmethod
    def get_Viewport(self, mainwindow) -> QFrame:
        """returns Frame for displaying in Viewport"""
        frame = QFrame()
        gridLayout = QGridLayout(frame)
        gridLayout.setObjectName(u"gridLayout_Viewport")
        label = QLabel(self.name)
        gridLayout.addWidget(label, 0, 0, Qt.AlignTop, Qt.AlignmentFlag.AlignLeft)
        label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        return frame

    def convertCvImage2QtImage(self, img):
        """converts Calculated Images to Qt Pixmaps for displayin on GUI"""
        rgb_image = Image.fromarray((img * 255).astype(np.uint8))
        qim = ImageQt(rgb_image)
        pixMap = QPixmap.fromImage(qim)
        return pixMap


class loadHyperCube(function):
    """Loads Hyper Cupe from *.BIL and *.HDR File"""

    def __init__(self):
        function.__init__(self)
        self.name = "Load Hyper Cube"
        self.input_count = 0
        self.output_count = 1
        self.dir = ""
        self.frame = None
        self.infoText = ""
        self.info = f'{self.name}\n\nSelect Hyperspectral Cube\nsupported datastructures: *.BIL\n'

        #self.info = "test"
    def run(self):
        self.output_value = envi.open(self.dir[0:len(str(self.dir)) - 4] + ".hdr", self.dir)
        self.infoText = open(self.dir[0:len(str(self.dir)) - 4] + ".hdr", "r").read()
        return True

    def get_Viewport(self, mainwindow) -> QFrame:
        self.frame = QFrame()
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout_Viewport")
        # adds Label with Function name (Top left Corner)
        label = QLabel()
        self.gridLayout.addWidget(label, 0, 0)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop | Qt.AlignLeading)
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        label.setText(self.info)

        # adds Label to Inform about Selection action
        InfoLoadLabel = QLabel("Select directory:")
        self.gridLayout.addWidget(InfoLoadLabel, 1, 0)
        InfoLoadLabel.setAlignment(Qt.AlignLeading | Qt.AlignLeft)

        # adds output Line for Displaying File Path
        self.DirText = QLineEdit()
        self.DirText.setText(self.dir)
        self.gridLayout.addWidget(self.DirText, 1, 1)

        # adds load button for choosing Filepath
        btn_load = QPushButton(self.frame)
        self.gridLayout.addWidget(btn_load, 2, 0)
        btn_load.setText("open")
        # connects Action for Button Press
        btn_load.pressed.connect(self.openfileDialog)

        # add Spacer Item
        horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout.addItem(horizontalSpacer, 4, 0, 1, 1)

        if self.infoText != "":
            textBrowser = QTextBrowser()
            textBrowser.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
            self.gridLayout.addWidget(textBrowser, 3, 0, 2, 2)
            textBrowser.setText(self.infoText)

        return self.frame

    def openfileDialog(self):
        """Opens File Dialog For one existing *.BIL File """
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilter("BILFILES(*.bil)")
        dialog.show()
        if dialog.exec():
            filenames = dialog.selectedFiles()
            self.dir = filenames[0]
            self.DirText.setText(self.dir)
            return filenames


class displayRGB(function):
    """Displays Provided Hypercupe as RGB Image(with option to Modify displayed Wavelengths)"""

    def __init__(self):
        function.__init__(self)
        self.name = "Display RGB"
        self.input_count = 1
        self.output_count = 0
        self.frame = None
        self.RGB = None
        self.bands = None
        self.hsObj = None
        self.RGB_Bands = [744, 422, 87]  # Default Wavelength from HypX1

        self.info = (f'{self.name}\n'
                     f'\nFunction for extracting RGB Values from Hyperspectral Cube und displaying them.\n'
                     f'Assign specific wavelength to RGB channels\n'
                     f'\nInstructions:\n'
                     f'1. Assign new wavelength using the sliders at the bottom\n'
                     f'2. Update the RGB Picture using the "update" button')

    def debug(self):
        """Debug Option, for Testing only! If Enabled, Funktion works in stand alone"""
        # dir = "/Users/karlkuckelsberg/Desktop/Arbeit/HyperSpec/Ral/Bil/Teflon.bil"
        dir = "/Users/karlkuckelsberg/Desktop/Arbeit/HyperSpec/Bil/Full7.bil"
        self.hsObj = sp.envi.open(dir[0:len(dir) - 4] + ".hdr", dir)
        self.bands = self.hsObj.bands.centers
        self.input_value = self.hsObj

    def run(self):
        """Gets RGB Picture from provided Wavelength"""
        self.hsObj = self.input_value
        if self.Debug:
            self.debug()
        self.RGB = sp.get_rgb(self.input_value, self.RGB_Bands)

        return True

    def get_Viewport(self, mainwindow) -> QFrame:
        # Frame (Container)
        self.frame = QFrame()
        gridLayout = QGridLayout(self.frame)
        gridLayout.setObjectName(u"gridLayout_Viewport")

        # Headline Funktion name
        label = QLabel(self.name)
        label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)
        gridLayout.addWidget(label, 0, 0, 1, 8)

        # Label for displaying Image
        self.lbl_pic = QLabel()
        self.lbl_pic.setAlignment(Qt.AlignLeading | Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_pic.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_pic.setAlignment(Qt.AlignLeading | Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_pic.resizeEvent = self.resizeLbl

        # check if Image Data were provided and display the Data
        if type(self.RGB) != type(None):
            label = QLabel(self.name)
            self.bands = self.input_value.bands.centers

            # Adds ScrollArea for Scaling Image Label
            self.scrollArea = QScrollArea()
            self.scrollArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            gridLayoutInner = QGridLayout(self.scrollArea)
            gridLayoutInner.addWidget(self.lbl_pic, 0, 0)
            gridLayoutInner.setContentsMargins(0, 0, 0, 0)

            gridLayout.addWidget(self.scrollArea, 1, 0, 1, 9)

            # Red Slider
            self.sl_Red = QSlider()
            self.lb_Red = QLabel("Red:")
            self.lb_Red_Min = QLabel()
            self.lb_Red_Val = QLabel()
            self.lb_Red_Max = QLabel()
            self.sl_Red.setOrientation(Qt.Horizontal)
            # Green Slider
            self.sl_Green = QSlider()
            self.lb_Green = QLabel("Green:")
            self.lb_Green_Min = QLabel()
            self.lb_Green_Val = QLabel()
            self.lb_Green_Max = QLabel()
            self.sl_Green.setOrientation(Qt.Horizontal)
            # Blue Slider
            self.sl_Blue = QSlider()
            self.lb_Blue = QLabel("Blue:")
            self.lb_Blue_Min = QLabel()
            self.lb_Blue_Val = QLabel()
            self.lb_Blue_Max = QLabel()
            self.sl_Blue.setOrientation(Qt.Horizontal)
            # update Button
            self.btn_update = QPushButton()
            self.btn_update.setText("update")

            # reset Button
            self.btn_RGB_reset = QPushButton()
            self.btn_RGB_reset.setText("reset RGB Values")

            # Set Slider Values
            self.sl_Red.setMinimum(0)
            self.sl_Red.setMaximum(len(self.bands) - 1)
            self.sl_Green.setMinimum(0)
            self.sl_Green.setMaximum(len(self.bands) - 1)
            self.sl_Blue.setMinimum(0)
            self.sl_Blue.setMaximum(len(self.bands) - 1)

            self.sl_Red.setValue(self.RGB_Bands[0])
            self.sl_Green.setValue(self.RGB_Bands[1])
            self.sl_Blue.setValue(self.RGB_Bands[2])

            # set Label Values
            self.lb_Red_Min.setText(str(round(self.bands[0], 2)))
            self.lb_Green_Min.setText(str(round(self.bands[0], 2)))
            self.lb_Blue_Min.setText(str(round(self.bands[0], 2)))

            self.lb_Red_Max.setText(str(round(self.bands[len(self.bands) - 1], 2)))
            self.lb_Green_Max.setText(str(round(self.bands[len(self.bands) - 1], 2)))
            self.lb_Blue_Max.setText(str(round(self.bands[len(self.bands) - 1], 2)))

            self.lb_Red_Val.setText(str(round(self.bands[self.sl_Red.value()], 2)))
            self.lb_Green_Val.setText(str(round(self.bands[self.sl_Green.value()], 2)))
            self.lb_Blue_Val.setText(str(round(self.bands[self.sl_Blue.value()], 2)))

            # set Label Orientation
            self.lb_Red_Val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lb_Green_Val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lb_Blue_Val.setAlignment(Qt.AlignmentFlag.AlignCenter)

            self.lb_Red_Max.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
            self.lb_Green_Max.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)
            self.lb_Blue_Max.setAlignment(
                Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTrailing | Qt.AlignmentFlag.AlignVCenter)

            # set GridLayout Sliders and Labels + Spacers
            gridLayout.addWidget(self.sl_Red, 5, 0, 1, 3)
            gridLayout.addWidget(self.sl_Green, 5, 3, 1, 3)
            gridLayout.addWidget(self.sl_Blue, 5, 6, 1, 3)

            gridLayout.addWidget(self.lb_Red, 4, 0, 1, 3)
            gridLayout.addWidget(self.lb_Green, 4, 3, 1, 3)
            gridLayout.addWidget(self.lb_Blue, 4, 6, 1, 3)

            gridLayout.addWidget(self.lb_Red_Min, 6, 0)
            gridLayout.addWidget(self.lb_Red_Val, 6, 1)
            gridLayout.addWidget(self.lb_Red_Max, 6, 2)

            gridLayout.addWidget(self.lb_Green_Min, 6, 3)
            gridLayout.addWidget(self.lb_Green_Val, 6, 4)
            gridLayout.addWidget(self.lb_Green_Max, 6, 5)

            gridLayout.addWidget(self.lb_Blue_Min, 6, 6)
            gridLayout.addWidget(self.lb_Blue_Val, 6, 7)
            gridLayout.addWidget(self.lb_Blue_Max, 6, 8)

            gridLayout.addWidget(self.btn_update, 7, 7, 1, 2)
            gridLayout.addWidget(self.btn_RGB_reset, 7, 5, 1, 2)

            # converts/scales Image for display
            self.pixmap = self.convertCvImage2QtImage(self.RGB)
            w = self.lbl_pic.width()
            h = self.lbl_pic.height()
            self.pixmap = self.pixmap.scaled(w, h, Qt.KeepAspectRatio)

            # adds Image to Label
            self.lbl_pic.setPixmap(self.pixmap)

            # self.lbl_pic.setStyleSheet("QLabel {background-color: red; color blue; }")
            # self.frame.setStyleSheet("QFrame {background-color: blue;}")

            self.lbl_pic.show()

            # callback functions
            self.btn_update.pressed.connect(self.slider_update)
            self.btn_RGB_reset.pressed.connect(self.resetRGB)

            self.sl_Red.valueChanged.connect(self.updateSliderLabel)
            self.sl_Green.valueChanged.connect(self.updateSliderLabel)
            self.sl_Blue.valueChanged.connect(self.updateSliderLabel)

        else:
            label.setText(self.info)

        return self.frame

    def resizeLbl(self, e):
        """Rezieze Funktion, for rezising Label by draging the Window"""
        w = self.lbl_pic.width()
        h = self.lbl_pic.height()

        pm = self.pixmap.scaled(w, h, Qt.KeepAspectRatio)

        self.lbl_pic.setPixmap(pm)

    def resetRGB(self):
        """Function call for reset Button // Resets RGB Values to predefined Default Values"""
        self.RGB_Bands = [744, 422, 87]
        self.sl_Red.setValue(self.RGB_Bands[0])
        self.sl_Green.setValue(self.RGB_Bands[1])
        self.sl_Blue.setValue(self.RGB_Bands[2])
        self.slider_update()

    def slider_update(self):
        """Updates Slider Labels and RGB Picture"""

        self.lb_Red_Val.setText(str(round(self.bands[self.sl_Red.value()], 2)))
        self.lb_Green_Val.setText(str(round(self.bands[self.sl_Green.value()], 2)))
        self.lb_Blue_Val.setText(str(round(self.bands[self.sl_Blue.value()], 2)))

        self.RGB_Bands = [self.sl_Red.value(), self.sl_Green.value(), self.sl_Blue.value()]

        w = self.lbl_pic.width()
        h = self.lbl_pic.height()
        self.RGB = sp.get_rgb(self.input_value, self.RGB_Bands)
        self.pixmap = self.convertCvImage2QtImage(self.RGB)

        self.pixmap = self.pixmap.scaled(w, h, Qt.KeepAspectRatio)
        self.lbl_pic.setPixmap(self.pixmap)
        self.lbl_pic.show()

    def updateSliderLabel(self):
        """Function for updating the current Slider Label"""
        self.lb_Red_Val.setText(str(round(self.bands[self.sl_Red.value()], 2)))
        self.lb_Green_Val.setText(str(round(self.bands[self.sl_Green.value()], 2)))
        self.lb_Blue_Val.setText(str(round(self.bands[self.sl_Blue.value()], 2)))


class extractSpectrum(function):
    """Extracts Point Spectrum from HyperCupe and Plots Spectrum"""

    def __init__(self):
        function.__init__(self)
        self.name = "extractSpectrum"
        self.input_count = 1
        self.output_count = 0
        self.RGB_Values = [744, 422, 87]
        self.frame = None
        self.position = []

        self.PlotData = None
        self.SpyArray = None

        self.isRect = False
        self.mouseMovePos = [[], []]
        # self.mouseMovePos.append([0,0])

        self.info = (f'{self.name}\n'
                     f'\nFunction for plotting and extracting wavelength per pixel or pixel region\n'
                     f'\nInstructions:\n'
                     f'1. Select data via clicking on the Picture (Point Spectrum) or Dragging a rectangle (Avarage Area Spectrum)\n'
                     f'2. Add Plots to plotbrowser (bottom right) via "add" button\n'
                     f'3. export all added plots via "export" button (*.CSV File for further processing)')

    def debug(self):
        """Debug Option, for Testing only!// Works as stand onlone function"""
        # dir = "/Users/karlkuckelsberg/Desktop/Arbeit/HyperSpec/Ral/Bil/Teflon.bil"
        dir = "/Users/karlkuckelsberg/Desktop/Arbeit/HyperSpec/Bil/Full7.bil"
        self.hsObj = sp.envi.open(dir[0:len(dir) - 4] + ".hdr", dir)

        self.input_value = self.hsObj

    def get_Viewport(self, mainwindow) -> QFrame:
        self.mainwindow = mainwindow
        self.frame = QFrame()
        gridLayout = QGridLayout(self.frame)
        gridLayout.setObjectName(u"gridLayout_Viewport")

        label = QLabel(self.name)
        gridLayout.addWidget(label, 0, 0, 1, 1)
        label.setAlignment(Qt.AlignLeading | Qt.AlignLeft | Qt.AlignTop)

        if type(self.PlotData) != type(None):
            self.lbl_pic = QLabel()
            scrollArea = QScrollArea()
            gridLayoutInner = QGridLayout(scrollArea)

            scrollArea.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            # scrollArea.setBackgroundRole(QPalette.ColorRole.Dark)
            scrollArea.setContentsMargins(0, 0, 0, 0)

            gridLayoutInner.addWidget(self.lbl_pic, 0, 0, 1, 1)
            gridLayoutInner.setContentsMargins(0, 0, 0, 0)
            gridLayout.addWidget(scrollArea, 1, 0, 2, 1)

            self.lbl_pic.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
            self.lbl_pic.setAlignment(Qt.AlignLeading | Qt.AlignmentFlag.AlignCenter | Qt.AlignmentFlag.AlignVCenter)

            # set RGB Picture to pixmap and aplly to label
            self.pixmap = self.convertCvImage2QtImage(sp.get_rgb(self.hsObj, self.RGB_Values))
            w = self.lbl_pic.width()
            h = self.lbl_pic.height()
            pm = self.pixmap.scaled(w, h, Qt.KeepAspectRatio)

            self.lbl_pic.setPixmap(pm)
            self.position = [int(self.pixmap.width() / 2), int(self.pixmap.height() / 2)]

            # Plot Widget
            self.figure = plt.figure()  # dpi=80
            self.canvas = FigureCanvasQTAgg(self.figure)
            self.canvas.draw()
            # self.canvas.setSizePolicy( QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
            # self.canvas.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
            self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

            horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)

            gridLayout.addItem(horizontalSpacer, 2, 1, 1, 1)

            self.scrollAreaPlot = QScrollArea()
            gridLayoutInnerPlot = QGridLayout(self.scrollAreaPlot)
            gridLayoutInnerPlot.addWidget(self.canvas, 0, 0)
            gridLayoutInnerPlot.setContentsMargins(0, 0, 0, 0)

            gridLayout.addWidget(self.scrollAreaPlot, 1, 1, 1, 1)

            self.plotFrame = QFrame()
            self.gridLayoutInnerFrame = QGridLayout(self.plotFrame)
            gridLayout.addWidget(self.plotFrame, 2, 1, 1, 1)
            self.plotFrame.setContentsMargins(0, 0, 0, 0)
            self.gridLayoutInnerFrame.setContentsMargins(0, 0, 0, 0)

            self.plotTree = QTreeWidget()
            self.plotTree.header().setVisible(False)
            self.plotTree.setSelectionMode(QAbstractItemView.ExtendedSelection)
            self.plotTree.setSelectionBehavior(QAbstractItemView.SelectItems)
            btn_add = QPushButton("add")
            btn_del = QPushButton("delete")
            btn_export = QPushButton("export")

            self.gridLayoutInnerFrame.addWidget(self.plotTree, 1, 0, 1, 2)
            self.gridLayoutInnerFrame.addWidget(btn_add, 2, 0, 1, 1)
            self.gridLayoutInnerFrame.addWidget(btn_del, 2, 1, 1, 1)
            self.gridLayoutInnerFrame.addWidget(btn_export, 0, 1, 1, 1)

            btn_add.pressed.connect(self.addPlot)
            btn_del.pressed.connect(self.delPlot)
            btn_export.pressed.connect(self.openfileDialog)

            self.drawCurrentLines()

            # Event Listeners
            self.lbl_pic.mousePressEvent = self.mouseevent
            self.lbl_pic.resizeEvent = self.resizeLbl
            self.updatePlot()

            self.lbl_pic.mouseMoveEvent = self.mousemoveevent
            self.lbl_pic.mouseReleaseEvent = self.mousereleaseevent

            # self.lbl_pic.setStyleSheet("QLabel {background-color: red; color blue; }")

        else:
            label.setText(self.info)

        return self.frame

    def exportData(self, dir: str):
        """Function to Export Plotted Data to csv File"""

        # open file
        f = open(dir, 'w')
        # start CSV writer
        writer = csv.writer(f)
        # writes Band Values
        writer.writerow(self.hsObj.bands.centers)
        data = []

        # adds all VAlues of added Plots from Plot Tree
        if self.plotTree.topLevelItemCount() > 0:
            for i in range(self.plotTree.topLevelItemCount()):
                item = self.plotTree.topLevelItem(i)
                data.append(np.array(item.data(0, Qt.ItemDataRole.UserRole)))
                #print(f'data number:{i}')
            writer.writerows(data)
        # in case of no plots in Plot tree, save single selected PlotData
        else:
            writer.writerow(np.array(self.PlotData))
        # close file
        f.close()

    def openfileDialog(self):
        """Button Callback(save File)
        Opens File save Dialog for one *csv file d """
        dialog = QFileDialog()
        filename = dialog.getSaveFileName(dialog, "Save File", "", "CSV (*.csv)")
        self.exportData(filename[0])

    def mousereleaseevent(self, e):
        """Mouse Relese for checking if Rectangle were selected"""
        if self.isRect:
            data = self.calcPlotDataRectangle()

            self.PlotData = data
            self.updatePlot()

    def calcPlotDataRectangle(self):
        """calculates Average about Values in selected Rectangle"""
        start = self.mouseMovePos[0]
        start_x = start[0]
        start_y = start[1]
        end = self.mouseMovePos[1]
        end_x = end[0]
        end_y = end[1]
        # Check if all points were selected
        if len(start) != 2 or len(end) != 2:
            return
        # get start and end points
        if start_x < end_x:
            topLeft_x = start_x
            bottomRight_x = end_x
        else:
            topLeft_x = end_x
            bottomRight_x = start_x

        if start_y < end_y:
            topLeft_y = start_y
            bottomRight_y = end_y
        else:
            topLeft_y = end_y
            bottomRight_y = start_y

        # get Vales of first Pixel
        liste = np.array(self.SpyArray[int(topLeft_y), int(topLeft_x)])

        # calculates Sum about all other points
        for x in range(int(bottomRight_x - topLeft_x)):
            for y in range(int(bottomRight_y - topLeft_y)):

                # in case of first point
                if x == 0 and y == 0:
                    pass
                else:
                    liste = [(i + j) for i, j in
                             zip(liste, np.array(self.SpyArray[int(topLeft_y + y), int(topLeft_x + x)]))]

        # divides Sum about all selected points
        liste = [i / (int(bottomRight_x - topLeft_x) * int(bottomRight_y - topLeft_y)) for i in liste]
        return liste

    def mousemoveevent(self, e):
        """Track Mouse movment and store first and last position"""
        w_p = self.lbl_pic.pixmap().width()
        h_p = self.lbl_pic.pixmap().height()
        w_l = self.lbl_pic.width()
        h_l = self.lbl_pic.height()

        ##Pixmapbereich berechnen

        dif = w_l - w_p
        left_site = dif / 2

        dif = h_l - h_p
        top_site = dif / 2

        if e.x() > left_site and e.x() < left_site + w_p and e.y() > top_site and e.y() < top_site + h_p:

            x_orig = (e.x() - left_site) * ((self.pixmap.width()) / (self.lbl_pic.width() - 2 * left_site))
            y_orig = (e.y() - top_site) * ((self.pixmap.height()) / (self.lbl_pic.height() - 2 * top_site))

            # first Position
            if not self.isRect:
                self.mouseMovePos[0] = [x_orig, y_orig]

            # last Position
            else:
                self.mouseMovePos[1] = [x_orig, y_orig]
                self.drawrectangle()

            self.isRect = True
        # print(self.mouseMovePos)

    def addPlot(self):
        """Button Callback for adding Plots to Plottree"""

        # create Tree Item
        treeItem = QTreeWidgetItem()
        if self.plotTree.topLevelItemCount() >= 1:
            current_plot_number = int((self.plotTree.topLevelItem(self.plotTree.topLevelItemCount() - 1)).text(0)[5::])
            treeItem.setText(0, f'Plot {current_plot_number + 1}')
        else:
            treeItem.setText(0, f'Plot {1}')

        # define Color
        color = [random.random(), random.random(), random.random()]
        # color = [random.randint(0,255),random.randint(0,255),random.randint(0,255)]

        # add Data to Tree Item
        treeItem.setData(0, Qt.ItemDataRole.UserRole, self.PlotData)
        treeItem.setData(1, Qt.ItemDataRole.UserRole, color)
        treeItem.setBackground(0, QColor(int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)))

        # add Tree Item
        self.plotTree.addTopLevelItem(treeItem)

    def delPlot(self):
        """Button Callback for deleting Plots to Plottree"""

        tree = self.plotTree
        root = tree.invisibleRootItem()
        # loops throu selected itmes and their children of Main Tree
        for item in tree.selectedItems():
            # removes items
            (item.parent() or root).removeChild(item)

    def resizeLbl(self, e):
        """Rezieze Funktion, for rezising Label by draging the Window"""
        w = self.lbl_pic.width()
        h = self.lbl_pic.height()

        pm = self.pixmap.scaled(w, h, Qt.KeepAspectRatio)

        self.lbl_pic.setPixmap(pm)

        if self.isRect:
            self.drawrectangle()
        else:
            self.drawCurrentLines()

        self.updatePlot()

    def mouseevent(self, e):
        """Detects Mouse events on Label and calculates position on pixmap, for displaying Plot at cklicked point"""

        # print(f'MouseEvent: {e}')

        w_p = self.lbl_pic.pixmap().width()
        h_p = self.lbl_pic.pixmap().height()
        w_l = self.lbl_pic.width()
        h_l = self.lbl_pic.height()

        ##Pixmapbereich berechnen

        dif = w_l - w_p
        left_site = dif / 2

        dif = h_l - h_p
        top_site = dif / 2

        if e.x() > left_site and e.x() < left_site + w_p and e.y() > top_site and e.y() < top_site + h_p:
            self.isRect = False
            x_orig = (e.x() - left_site) * ((self.pixmap.width()) / (self.lbl_pic.width() - 2 * left_site))
            y_orig = (e.y() - top_site) * ((self.pixmap.height()) / (self.lbl_pic.height() - 2 * top_site))
            self.position = [int(x_orig), int(y_orig)]
            # print(f'x: {int(x_orig)}; y: {int(y_orig)}')
            # print(f'w_pixmap: {w_p}; w_lbl: {w_l}; w_site: {left_site}; x_maus: {e.x()}; x_calc: {e.x() - left_site}')
            self.drawCurrentLines()

            self.PlotData = self.SpyArray[int(y_orig), int(x_orig)]
            self.updatePlot()

    def updatePlot(self):
        """Updates Plot View with existing Plot data """

        plt.subplots_adjust(left=0.2, right=0.95, bottom=0.2, top=0.95)

        self.figure.clear()
        bands = self.hsObj.bands.centers
        values = self.PlotData

        plt.plot(bands, values, color="red")

        for i in range(self.plotTree.topLevelItemCount()):
            item = self.plotTree.topLevelItem(i)
            data = item.data(0, Qt.ItemDataRole.UserRole)
            color = item.data(1, Qt.ItemDataRole.UserRole)
            plt.plot(bands, data, color=color)

        xmin, xmax, ymin, ymax = plt.axis()
        plt.vlines(self.hsObj.bands.centers[self.RGB_Values[0]], 0, ymax, colors="red")
        plt.vlines(self.hsObj.bands.centers[self.RGB_Values[1]], 0, ymax, colors="green")
        plt.vlines(self.hsObj.bands.centers[self.RGB_Values[2]], 0, ymax, colors="blue")
        plt.xlabel(f'{"Wavelength in "}{self.hsObj.bands.band_unit}')
        plt.ylabel("Intensity")

        self.canvas.draw()

    def drawrectangle(self):
        start = self.mouseMovePos[0]
        end = self.mouseMovePos[1]

        pm = self.pixmap.copy(0, 0, self.pixmap.width(), self.pixmap.height())

        painter = QtGui.QPainter(pm)
        pen = QtGui.QPen()

        pen.setWidth(3)
        pen.setColor(QtGui.QColor('red'))
        ####
        painter.setPen(pen)
        painter.setBrush(QtGui.QColor(255, 0, 0, 100))

        painter.drawRect(start[0], start[1], end[0] - start[0], end[1] - start[1])
        painter.end()
        ###
        w = self.lbl_pic.width()
        h = self.lbl_pic.height()
        pm = pm.scaled(w, h, QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.lbl_pic.setPixmap(pm)
        self.lbl_pic.show()

    def drawCurrentLines(self):
        """Draws Red lines at the given Point """

        # print(f'X: {x}; Y: {y}; lbl_width: {self.pixmap.width()}; lbl_height: {self.pixmap.height()}')

        pm = self.pixmap.copy(0, 0, self.pixmap.width(), self.pixmap.height())

        painter = QtGui.QPainter(pm)
        pen = QtGui.QPen()
        pen.setWidth(3)
        pen.setColor(QtGui.QColor('red'))
        painter.setPen(pen)

        painter.drawLine(self.position[0], 0, self.position[0], self.hsObj.nrows)

        painter.drawLine(0, self.position[1], self.hsObj.ncols, self.position[1])
        painter.end()

        w = self.lbl_pic.width()
        h = self.lbl_pic.height()
        pm = pm.scaled(w, h, QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.lbl_pic.setPixmap(pm)
        self.lbl_pic.show()

    def run(self):
        """Calculates Plot Data for given Point"""
        if self.Debug:
            self.debug()

        self.hsObj = self.input_value
        y = int(self.input_value.nrows / 2)
        x = int(len(self.input_value.bands.centers) / 2)

        self.SpyArray = sp.SpyFile.load(self.input_value)

        self.PlotData = self.SpyArray[x, y]
        # print(self.PlotData)

        return True


if __name__ == "__main__":
    pass
