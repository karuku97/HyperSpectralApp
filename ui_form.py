# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'form.ui'
##
## Created by: Qt User Interface Compiler version 6.5.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QFrame, QGridLayout,
    QHeaderView, QLabel, QMainWindow, QMenuBar,
    QPushButton, QSizePolicy, QSpacerItem, QStatusBar,
    QTreeWidget, QTreeWidgetItem, QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(883, 627)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setSpacing(5)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setContentsMargins(5, 5, 5, 5)
        self.frame = QFrame(self.centralwidget)
        self.frame.setObjectName(u"frame")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setFrameShape(QFrame.StyledPanel)
        self.frame.setFrameShadow(QFrame.Raised)
        self.gridLayout_3 = QGridLayout(self.frame)
        self.gridLayout_3.setSpacing(5)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.gridLayout_3.setContentsMargins(5, 5, 5, 5)
        self.label = QLabel(self.frame)
        self.label.setObjectName(u"label")

        self.gridLayout_3.addWidget(self.label, 0, 0, 1, 1)

        self.tree_main = QTreeWidget(self.frame)
        __qtreewidgetitem = QTreeWidgetItem()
        __qtreewidgetitem.setText(0, u"1");
        self.tree_main.setHeaderItem(__qtreewidgetitem)
        self.tree_main.setObjectName(u"tree_main")
        sizePolicy1 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(1)
        sizePolicy1.setHeightForWidth(self.tree_main.sizePolicy().hasHeightForWidth())
        self.tree_main.setSizePolicy(sizePolicy1)
        self.tree_main.setFrameShape(QFrame.StyledPanel)
        self.tree_main.setFrameShadow(QFrame.Sunken)
        self.tree_main.setMidLineWidth(1)
        self.tree_main.setEditTriggers(QAbstractItemView.DoubleClicked|QAbstractItemView.EditKeyPressed)
        self.tree_main.setDragEnabled(True)
        self.tree_main.setDragDropOverwriteMode(False)
        self.tree_main.setDragDropMode(QAbstractItemView.DropOnly)
        self.tree_main.setDefaultDropAction(Qt.MoveAction)
        self.tree_main.setAlternatingRowColors(False)
        self.tree_main.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.tree_main.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.tree_main.setRootIsDecorated(True)
        self.tree_main.setColumnCount(1)
        self.tree_main.header().setVisible(False)

        self.gridLayout_3.addWidget(self.tree_main, 1, 0, 1, 1)


        self.gridLayout.addWidget(self.frame, 2, 0, 1, 1)

        self.btn_delete = QPushButton(self.centralwidget)
        self.btn_delete.setObjectName(u"btn_delete")

        self.gridLayout.addWidget(self.btn_delete, 0, 3, 1, 1)

        self.btn_libraryBrowser = QPushButton(self.centralwidget)
        self.btn_libraryBrowser.setObjectName(u"btn_libraryBrowser")

        self.gridLayout.addWidget(self.btn_libraryBrowser, 0, 5, 1, 1)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.gridLayout.addItem(self.horizontalSpacer, 0, 6, 1, 1)

        self.btn_connect = QPushButton(self.centralwidget)
        self.btn_connect.setObjectName(u"btn_connect")

        self.gridLayout.addWidget(self.btn_connect, 0, 4, 1, 1)

        self.btn_start = QPushButton(self.centralwidget)
        self.btn_start.setObjectName(u"btn_start")
        sizePolicy2 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.btn_start.sizePolicy().hasHeightForWidth())
        self.btn_start.setSizePolicy(sizePolicy2)

        self.gridLayout.addWidget(self.btn_start, 0, 0, 1, 1)

        self.frm_viewport = QFrame(self.centralwidget)
        self.frm_viewport.setObjectName(u"frm_viewport")
        sizePolicy3 = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.frm_viewport.sizePolicy().hasHeightForWidth())
        self.frm_viewport.setSizePolicy(sizePolicy3)
        self.frm_viewport.setFrameShape(QFrame.StyledPanel)
        self.frm_viewport.setFrameShadow(QFrame.Raised)
        self.gridLayout_2 = QGridLayout(self.frm_viewport)
        self.gridLayout_2.setSpacing(0)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)

        self.gridLayout.addWidget(self.frm_viewport, 2, 2, 1, 5)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 883, 24))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Hyper Spektral APP", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Run Diagram:", None))
        self.btn_delete.setText(QCoreApplication.translate("MainWindow", u"delete", None))
        self.btn_libraryBrowser.setText(QCoreApplication.translate("MainWindow", u"Library Browser", None))
        self.btn_connect.setText(QCoreApplication.translate("MainWindow", u"connect", None))
        self.btn_start.setText(QCoreApplication.translate("MainWindow", u"Start", None))
    # retranslateUi

