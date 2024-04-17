import copy
import os
from abc import ABC, abstractmethod

import cv2
import spectral.image
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
                               QFileDialog, QSlider, QSpacerItem, QScrollArea, QTextBrowser,QTabWidget,QTableWidgetItem)

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvasQTAgg
import matplotlib.pyplot as plt

from spectral import envi
import spectral as sp
import cv2 as cv
from PIL import Image
from PIL.ImageQt import ImageQt
import numpy as np
import bisect
import matplotlib.pyplot as plt
import random
import csv
import kira_image_capture as kic


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
        self.Debug = False

        #self.info = "test"

    def debug(self):
        """Debug Option, for Testing only! If Enabled, Funktion works in stand alone"""

        self.dir = "C:/Users/karlk/Desktop/Arbeit/HyperSpec/Bil/Full7.bil"

    def run(self):
        if self.dir == "": return "Kein Pfad angegeben"
        #try:
        if self.Debug:
            self.debug()
        file_path = self.dir[0:len(str(self.dir)) - 4] + ".hdr"
        #print(file_path)
        self.output_value = envi.open(file_path, self.dir)

        self.infoText = open(file_path, "r").read()
        return True
        #except:
           # return "Verbindung fehlt oder Fehlerhaft"

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
class captureHyperCube(function):
    def __init__(self):
        function.__init__(self)
        self.name = "capture Hypercube"
        self.input_count = 0
        self.output_count = 1
        self.dir = ""
        self.frame = None
        self.infoText = ""
        self.info = f'{self.name}\n\ncapture Hyperspectralcube using Hyperspectral Kamera.\n'
        self.Debug = True
        self.isInit = False

        self.numOfLines = 20
        self.filename = "testCap"
        self.filepath = "C:/Users/karlk/Desktop/Arbeit/"
        self.expTime = 83500

        self.CM = None

        self.Basler = kic.Basler



        #self.info = "test"

    def __del__(self):
        if self.CM != None:
            self.CM.remove_camera(self.SN)


    def debug(self):
        """Debug Option, for Testing only! If Enabled, Funktion works in stand alone"""
        os.environ["PYLON_CAMEMU"] = "1"
        #print(os.environ["PYLON_CAMEMU"])


    def run(self):

        if not self.isInit:
            return "no initialized Camera"

        cube = self.CM.grab_hyperspec(self.Basler.SERIAL_NUMBER, self.numOfLines, 3, False, 1)
        meta = kic.HyperspecUtility.generate_metadata(self.CM.cameras[0], self.numOfLines, self.Basler.Y_OFFSET,
                                                      self.Basler.Y_BINNING, self.Basler.A, self.Basler.B,
                                                      self.Basler.C, 1)
        #print(os.path.isfile(f'{self.filepath}\{self.filename}.bil'))
        if self.output_value != None:
            del self.output_value


        kic.HyperspecUtility.write_cube(cube, meta, self.filepath, f'{self.filename}.hdr')


        self.output_value = envi.open(f'{self.filepath}\\{self.filename}.hdr',f"{self.filepath}\\{self.filename}.bil")
        #image = spectral.envi.create_image(f'{self.filepath}/{self.filename}.hdr',meta,force=True,interleave="bil",ext="bil",dtype=np.uint16)
        #mm = image.open_memmap(writable=True)
        #mm = cube
        #self.output_value = envi.SpectralLibrary(cube,meta)



        #image.bands = meta["wavelength"]


        #print(meta)

        return True



    def get_Viewport(self, mainwindow) -> QFrame:
        self.frame = QFrame()
        self.gridLayout = QGridLayout(self.frame)
        self.gridLayout.setObjectName(u"gridLayout_Viewport")
        # adds Label with Function name (Top left Corner)
        label = QLabel()
        self.gridLayout.addWidget(label, 0, 0,1,2)
        label.setAlignment(Qt.AlignLeft | Qt.AlignTop | Qt.AlignLeading)
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)
        label.setText(self.info)

        tabs = QTabWidget(self.frame)
        self.gridLayout.addWidget(tabs,1,0,1,2)


        # Tab Kamera
        tab_capture = QFrame()
        self.gridLayout_tcapture = QGridLayout(tab_capture)
        self.gridLayout_tcapture.setObjectName(u"gridLayout_TabKamera")
        tabs.addTab(tab_capture, "Capture Parameter")

        # Number of Lines
        # adds Label to Inform about Selection action
        lbl_NumOfLines = QLabel("Number of Lines:")
        self.gridLayout_tcapture.addWidget(lbl_NumOfLines, 0, 0)
        lbl_NumOfLines.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_NumOfLines = QLineEdit()
        self.led_NumOfLines.setText(str(self.numOfLines))
        self.gridLayout_tcapture.addWidget(self.led_NumOfLines, 0, 1)
        self.led_NumOfLines.textChanged.connect( self.applyValues)

        # Exposuretime
        # adds Label to Inform about Selection action
        lbl_expTime = QLabel("Exposuretime:")
        self.gridLayout_tcapture.addWidget(lbl_expTime, 1, 0)
        lbl_expTime.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_expTime = QLineEdit()
        self.led_expTime.setText(str(self.expTime))
        self.gridLayout_tcapture.addWidget(self.led_expTime, 1, 1)
        self.led_expTime.textChanged.connect(self.applyValues)

        # Filepath
        # adds Label to Inform about Selection action
        lbl_filepath = QLabel("Filepath:")
        self.gridLayout_tcapture.addWidget(lbl_filepath, 2, 0)
        lbl_filepath.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_filepath = QLineEdit()
        self.led_filepath.setText(self.filepath)
        self.gridLayout_tcapture.addWidget(self.led_filepath, 2, 1)
        self.led_filepath.textChanged.connect(self.applyValues)

        # filename
        # adds Label to Inform about Selection action
        lbl_filename = QLabel("Filename:")
        self.gridLayout_tcapture.addWidget(lbl_filename, 3, 0)
        lbl_filename.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_filename = QLineEdit()
        self.led_filename.setText(self.filename)
        self.gridLayout_tcapture.addWidget(self.led_filename, 3, 1)
        self.led_filename.textChanged.connect(self.applyValues)

        # add Spacer Item
        horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout_tcapture.addItem(horizontalSpacer, 4, 0, 1, 1)


        ### Kameraparameter
        tab_camera = QFrame()
        self.gridLayout_tcamera = QGridLayout(tab_camera)
        self.gridLayout_tcamera.setObjectName(u"gridLayout_TabKamera")
        tabs.addTab(tab_camera, "Camera Parameter")

        # Serialnumber
        # adds Label to Inform about Selection action
        lbl_SNNumber = QLabel("Serialnumber:")
        self.gridLayout_tcamera.addWidget(lbl_SNNumber, 0, 0)
        lbl_SNNumber.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_SNNumber = QLineEdit()
        self.led_SNNumber.setText(str(self.Basler.SERIAL_NUMBER))
        self.gridLayout_tcamera.addWidget(self.led_SNNumber, 0, 1)
        self.led_SNNumber.textChanged.connect(self.applyValues)

        # Width
        # adds Label to Inform about Selection action
        lbl_width = QLabel("Width:")
        self.gridLayout_tcamera.addWidget(lbl_width, 1, 0)
        lbl_width.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_width = QLineEdit()
        self.led_width.setText(str(self.Basler.ROI_WIDTH))
        self.gridLayout_tcamera.addWidget(self.led_width, 1, 1)
        self.led_width.textChanged.connect(self.applyValues)

        # Height
        # adds Label to Inform about Selection action
        lbl_height = QLabel("Height:")
        self.gridLayout_tcamera.addWidget(lbl_height, 2, 0)
        lbl_height.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_height = QLineEdit()
        self.led_height.setText(str(self.Basler.ROI_HEIGHT))
        self.gridLayout_tcamera.addWidget(self.led_height, 2, 1)
        self.led_height.textChanged.connect(self.applyValues)

        # Binning
        # adds Label to Inform about Selection action
        lbl_binning = QLabel("Binning:")
        self.gridLayout_tcamera.addWidget(lbl_binning, 3, 0)
        lbl_binning.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_binning = QLineEdit()
        self.led_binning.setText(str(self.Basler.Y_BINNING))
        self.gridLayout_tcamera.addWidget(self.led_binning, 3, 1)
        self.led_binning.textChanged.connect(self.applyValues)

        # X-Offset
        # adds Label to Inform about Selection action
        lbl_xoff = QLabel("X-Offset:")
        self.gridLayout_tcamera.addWidget(lbl_xoff, 4, 0)
        lbl_xoff.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_xoff = QLineEdit()
        self.led_xoff.setText(str(self.Basler.X_OFFSET))
        self.gridLayout_tcamera.addWidget(self.led_xoff, 4, 1)
        self.led_xoff.textChanged.connect(self.applyValues)

        # X-Offset
        # adds Label to Inform about Selection action
        lbl_yoff = QLabel("Y-Offset:")
        self.gridLayout_tcamera.addWidget(lbl_yoff, 5, 0)
        lbl_yoff.setAlignment(Qt.AlignLeading | Qt.AlignLeft)
        # adds output Line for Displaying File Path
        self.led_yoff = QLineEdit()
        self.led_yoff.setText(str(self.Basler.Y_OFFSET))
        self.gridLayout_tcamera.addWidget(self.led_yoff, 5, 1)
        self.led_yoff.textChanged.connect(self.applyValues)

        # add Spacer Item
        horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.gridLayout_tcamera.addItem(horizontalSpacer, 6, 0, 1, 1)



        # init Kamera
        btn_initCamera = QPushButton(self.frame)
        btn_initCamera.setText("Initialize Camera")
        self.gridLayout.addWidget(btn_initCamera, 3, 0)
        btn_initCamera.pressed.connect(self.initCamera)

        #testImage
        btn_testImage = QPushButton(self.frame)
        btn_testImage.setText("test Image")
        self.gridLayout.addWidget(btn_testImage,3,1)
        btn_testImage.pressed.connect(self.captureTestImage)

        self.lbl_testImage = QLabel()
        self.gridLayout.addWidget(self.lbl_testImage, 4,0 ,1 ,2)
        self.lbl_testImage.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.lbl_testImage.setAlignment(Qt.AlignmentFlag.AlignCenter)






        return self.frame

    def initCamera(self):
        if self.Debug : self.debug()
        if self.isInit: return "already Initialized"
        try:
            self.CM = kic.CameraManager()
            self.CM.add_cameras()
            self.CM.cameras[0].DeviceLinkThroughputLimitMode.SetValue("Off")

            self.SN = self.CM.cameras[0].GetDeviceInfo().GetSerialNumber()
            self.led_SNNumber.setText(str(self.SN))
            self.CM.set_camera_window(self.Basler.SERIAL_NUMBER, self.Basler.ROI_WIDTH, self.Basler.ROI_HEIGHT,self.Basler.X_OFFSET, self.Basler.Y_OFFSET, self.Basler.Y_BINNING)
            self.isInit = True

        except:
            return "Initit Error"


    def captureTestImage(self):
        img = self.CM.capture_frame(self.Basler.SERIAL_NUMBER)

        pixmap = self.convertCvImage2QtImage(img)
        w = self.lbl_testImage.width()
        h = self.lbl_testImage.height()
        pixmap = pixmap.scaled(w, h, Qt.KeepAspectRatio)

        # adds Image to Label
        self.lbl_testImage.setPixmap(pixmap)


    def applyValues(self):
        self.numOfLines = int(self.led_NumOfLines.text())
        self.expTime = int(self.led_expTime.text())
        if self.isInit:
            self.CM.set_exposure(self.Basler.SERIAL_NUMBER,int(self.led_expTime.text()))

        self.filepath = self.led_filepath.text()
        self.filename = self.led_filename.text()

        self.Basler.SERIAL_NUMBER = self.led_SNNumber.text()
        self.Basler.ROI_WIDTH = int(self.led_width.text())
        self.Basler.ROI_HEIGHT = int(self.led_height.text())
        self.Basler.Y_BINNING = int(self.led_binning.text())
        self.Basler.X_OFFSET = int(self.led_xoff.text())
        self.Basler.Y_OFFSET = int(self.led_yoff.text())


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
        self.SpyArray = None
        self.Debug = False

        self.info = (f'{self.name}\n'
                     f'\nFunction for extracting RGB Values from Hyperspectral Cube und displaying them.\n'
                     f'Assign specific wavelength to RGB channels\n'
                     f'\nInstructions:\n'
                     f'1. Assign new wavelength using the sliders at the bottom\n'
                     f'2. Update the RGB Picture using the "update" button')

    def debug(self):
        """Debug Option, for Testing only! If Enabled, Funktion works in stand alone"""
        # dir = "/Users/karlkuckelsberg/Desktop/Arbeit/HyperSpec/Ral/Bil/Teflon.bil"
        dir = "C:/Users/karlk/Desktop/Arbeit/BILProjekt/1920First.bil"
        self.input_value = sp.envi.open(dir[0:len(dir) - 4] + ".hdr", dir)
        self.bands = self.input_value.bands.centers


    def run(self):
        """Gets RGB Picture from provided Wavelength"""
        if self.Debug:
            self.debug()
            self.SpyArray = sp.SpyFile.load(self.input_value)
            self.calcRGB_Values()
            self.RGB = sp.get_rgb(self.input_value, self.RGB_Bands)
            return

        #try:
        self.input_value = self.input_point.output_value
        self.SpyArray = sp.SpyFile.load(self.input_value)
        del self.input_value
        self.input_value= None
        self.calcRGB_Values()

        self.RGB = sp.get_rgb(self.SpyArray, self.RGB_Bands)

        return True
        #except:
            #return "Verbindung fehlt oder Fehlerhaft"

    def calcRGB_Values(self):
        r  = (np.abs(np.asarray(self.SpyArray.bands.centers) - 640)).argmin()
        g = (np.abs(np.asarray(self.SpyArray.bands.centers) - 550)).argmin()
        b = (np.abs(np.asarray(self.SpyArray.bands.centers) - 460)).argmin()
        self.RGB_Bands = [r,g,b]

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
            self.bands = self.SpyArray.bands.centers

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
        self.RGB = sp.get_rgb(self.SpyArray, self.RGB_Bands)
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
        self.input_value = sp.envi.open(dir[0:len(dir) - 4] + ".hdr", dir)



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
            self.pixmap = self.convertCvImage2QtImage(sp.get_rgb(self.SpyArray, self.RGB_Values))
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
            self.scrollAreaPlot.setMaximumWidth(550)
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
        writer.writerow(self.input_value.bands.centers)
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
        bands = self.SpyArray.bands.centers
        values = self.PlotData

        plt.plot(bands, values, color="red")

        for i in range(self.plotTree.topLevelItemCount()):
            item = self.plotTree.topLevelItem(i)
            data = item.data(0, Qt.ItemDataRole.UserRole)
            color = item.data(1, Qt.ItemDataRole.UserRole)
            plt.plot(bands, data, color=color)

        xmin, xmax, ymin, ymax = plt.axis()
        plt.vlines(self.SpyArray.bands.centers[self.RGB_Values[0]], 0, ymax, colors="red")
        plt.vlines(self.SpyArray.bands.centers[self.RGB_Values[1]], 0, ymax, colors="green")
        plt.vlines(self.SpyArray.bands.centers[self.RGB_Values[2]], 0, ymax, colors="blue")
        plt.xlabel(f'{"Wavelength in "}{self.SpyArray.bands.band_unit}')
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

        painter.drawLine(self.position[0], 0, self.position[0], self.SpyArray.nrows)

        painter.drawLine(0, self.position[1], self.SpyArray.ncols, self.position[1])
        painter.end()

        w = self.lbl_pic.width()
        h = self.lbl_pic.height()
        pm = pm.scaled(w, h, QtCore.Qt.AspectRatioMode.KeepAspectRatio)

        self.lbl_pic.setPixmap(pm)
        self.lbl_pic.show()

    def calcRGB_Values(self):
        r  = (np.abs(np.asarray(self.SpyArray.bands.centers) - 640)).argmin()
        g = (np.abs(np.asarray(self.SpyArray.bands.centers) - 550)).argmin()
        b = (np.abs(np.asarray(self.SpyArray.bands.centers) - 460)).argmin()
        self.RGB_Values = [r,g,b]


    def run(self):
        """Calculates Plot Data for given Point"""
        #try:
        if self.Debug:
            self.debug()

        self.input_value = self.input_point.output_value


        self.SpyArray = sp.SpyFile.load(self.input_value)
        del self.input_value
        self.input_value = None

        self.calcRGB_Values()


        x = int(self.SpyArray.nrows / 2)
        y = int(len(self.SpyArray.bands.centers) / 2)

        self.PlotData = self.SpyArray[x, y]
        # print(self.PlotData)

        return True
        #except:
            #return "Verbindung fehlt oder Fehlerhaft"

if __name__ == "__main__":
    pass
