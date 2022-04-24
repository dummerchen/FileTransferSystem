# -*- coding:utf-8 -*-
# @Author : Dummerfu
# @Contact : https://github.com/dummerchen 
# @Time : 2022/4/23 22:36
from UI.MainWindow import Main_Window
from PySide6 import QtWidgets
import sys

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window=Main_Window()
    window.show()
    sys.exit(app.exec())