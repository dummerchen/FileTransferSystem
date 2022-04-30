# -*- coding:utf-8 -*-
# @Author : Dummerfu
# @Contact : https://github.com/dummerchen 
# @Time : 2022/4/23 22:36
from UI.MainWindow import Main_Window
from PySide6 import QtWidgets
import sys
import os
import PySide6

if __name__ == '__main__':
    dirpath=os.path.dirname(PySide6.__file__)
    plugin_path=os.path.join(dirpath,'plugin','platform')
    os.environ['QT_QPA_PLUGIN_PLATFORM_PATH']=plugin_path
    app = QtWidgets.QApplication(sys.argv)

    window=Main_Window()
    window.show()
    sys.exit(app.exec())