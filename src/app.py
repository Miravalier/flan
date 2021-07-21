#!/usr/bin/env python3.9
import sys

from PyQt5 import QtGui, QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication


class MainWindow(QMainWindow):
    def __init__(self):
        screenShape = QtWidgets.qApp.desktop().availableGeometry()

        QMainWindow.__init__(self)
        self.setWindowFlags(
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.X11BypassWindowManagerHint |
            QtCore.Qt.WindowTransparentForInput
        )
        self.setGeometry(
            QtWidgets.QStyle.alignedRect(
                QtCore.Qt.LeftToRight, QtCore.Qt.AlignCenter,
                QtCore.QSize(screenShape.width(), screenShape.height()),
                screenShape
        ))
        self.setAttribute(QtCore.Qt.WA_NoSystemBackground, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

    def paintEvent(self, event=None):
        # Create painter
        painter = QtGui.QPainter(self)

        # Paint rectangle
        painter.setOpacity(0.1)
        painter.setBrush(QtCore.Qt.white)
        painter.setPen(QtGui.QPen(QtCore.Qt.white))
        painter.drawRect(self.rect())

        # Paint text
        painter.setFont(QtGui.QFont("Ubuntu Sans", 12, QtGui.QFont.Bold))
        painter.setOpacity(0.7)
        painter.setPen(QtGui.QPen(QtCore.Qt.black))
        painter.drawText(QtCore.QPoint(50, 50), "Some text")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    app.exec_()
