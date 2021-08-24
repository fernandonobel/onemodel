#!/usr/bin/env python3
import sys

# importing required libraries
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtPrintSupport import *
import os

class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        # Set window geometry.
        self.setGeometry(0, 0, 1200, 800)

        # Move the window to the center of the screen.
        centerPoint = QDesktopWidget().availableGeometry().center()
        qtRectangle = self.frameGeometry()
        qtRectangle.moveCenter(centerPoint)
        self.move(qtRectangle.topLeft())

        # Create the layout. 
        grid_layout = QGridLayout()
        grid_layout.setColumnStretch(1, 2)

        # Create directory view.
        self.model = QFileSystemModel()
        self.model.setRootPath('')

        self.tree = QTreeView()
        self.tree.setModel(self.model)

        self.tree.setAnimated(False)
        self.tree.setIndentation(20)
        self.tree.setSortingEnabled(True)

        # Hide all columns, but name.
        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)

        # creating a QPlainTextEdit object
        self.editor = QLineEdit()
        grid_layout.addWidget(self.editor, 0, 0, 1, 3)

        grid_layout.addWidget(self.tree, 1, 0, 3, 1)

        # creating a QPlainTextEdit object
        self.editor = QPlainTextEdit()
        grid_layout.addWidget(self.editor, 1, 1, 1, 1)

        # creating a QPlainTextEdit object
        self.editor = QPlainTextEdit()
        grid_layout.addWidget(self.editor, 2, 1, 2, 1)

        # creating a QPlainTextEdit object
        self.editor = QPlainTextEdit()
        grid_layout.addWidget(self.editor, 1, 2, 3, 1)

        # creating a QWidget layout
        container = QWidget()

        # setting layout to the container
        container.setLayout(grid_layout)

        # making container as central widget
        self.setCentralWidget(container)

        # creating a status bar object
        self.status = QStatusBar()

        # setting stats bar to the window
        self.setStatusBar(self.status)

        # creating a file tool bar
        file_toolbar = QToolBar("File")

        # adding file tool bar to the window
        self.addToolBar(file_toolbar)

        # creating a file menu
        file_menu = self.menuBar().addMenu("&File")



        self.setWindowTitle('OneModel Editor')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
