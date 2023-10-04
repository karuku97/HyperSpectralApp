from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
                            QMetaObject, QObject, QPoint, QRect,
                            QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
                           QFont, QFontDatabase, QGradient, QIcon,
                           QImage, QKeySequence, QLinearGradient, QPainter,
                           QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QAbstractItemView, QApplication, QGridLayout, QHeaderView,
                               QMainWindow, QMenuBar, QPushButton, QSizePolicy,
                               QStatusBar, QTreeWidget, QTreeWidgetItem, QWidget, QFrame, QLabel)

import functions


class LibraryWindow(QWidget):
    """Library Window Class for creating the Library Window"""

    def __init__(self, parent=None):
        """Installation"""
        super().__init__(parent)

        # adds GridLayout to Window
        self.gridLayout = QGridLayout(self)
        self.gridLayout.setObjectName(u"gridLayout")

        # adds Headline To Window ( Top left corner )
        self.label = QLabel("Library: ")
        self.gridLayout.addWidget(self.label, 0, 0)

        # adds QTree Widget for displaying all Functions
        self.tree_second = QTreeWidget(self)
        self.tree_second.setObjectName(u"tree_second")
        # allows Drag Actions (no Drops)
        self.tree_second.setDragDropMode(QAbstractItemView.DragOnly)
        # sets Selection Method
        self.tree_second.setSelectionMode(QAbstractItemView.ExtendedSelection)
        # disable Visibility of Header Item
        self.tree_second.header().setVisible(False)

        # adds Tree Widget to GridLayout
        self.gridLayout.addWidget(self.tree_second, 1, 0)
        # sets ContentMargin of GridLayout
        self.gridLayout.setContentsMargins(5, 5, 5, 5)

        # sets Window Title
        self.setWindowTitle("Library Browser")

        # Function call to fill the Library with all funkctons
        self.fillLibrary()

    def fillLibrary(self):
        """Fills the QTree Widget with all funktions"""
        # List of all function, supossed to be shown
        list_of_fct = [functions.loadHyperCube(), functions.displayRGB(), functions.extractSpectrum()]
        # loop throu every function and adds Treewidget from function
        for fct in list_of_fct:
            self.tree_second.addTopLevelItem(fct.createTreeWidget())

    def closeEvent(self, e):
        """hides Window if it is supposed to be closed"""
        self.hide()


if __name__ == "__main__":
    pass
