# -*- coding:utf-8 -*-
# @Author : Dummerfu
# @Contact : https://github.com/dummerchen 
# @Time : 2022/4/15 15:51
import os
import sys
import time

from PySide6 import QtWidgets,QtCore,QtNetwork,QtGui
from PySide6.QtCore import Slot,Qt
from client_socket_no_ssl import Client,transfer_size
# CHECKED 多线程上传、下载文件
# CHECKED 多页面切换
# CHECKED 多线程进度条显示
# CHECKED 可同时选择多文件上传
# CHECKED 可同时选择多文件上传
# CHECKED 可显示服务器目录下的文件
# CHECKED 页面是文件大小或文件路径 (都是文件名和文件路径会不会更好？

# TODO about页面
# TODO 增加选择服务器路径 按钮

class Main_Window(QtWidgets.QMainWindow):
    def __init__(self):
        # TODO 右键菜单复制绝对路径
        # TODO 上传页面右键菜单进行删除
        super().__init__()
        self.setWindowTitle("文件传输系统")
        # h,w
        self.setFixedSize(564, 573)
        # 下载按钮
        self.tab_widget=QtWidgets.QTabWidget(self)
        self.tab_widget.setGeometry(QtCore.QRect(-1, -3, 568, 576))

        self.connectwidget=ConnectWidget(self)
        self.downloadwidget=DownloadWidget(self)
        self.uploadwidget=UpLoadWidget(self)

        self.tab_widget.addTab(self.connectwidget,'连接服务器')
        self.tab_widget.addTab(self.downloadwidget,'下载')
        self.tab_widget.addTab(self.uploadwidget, '上传')

        self.tab_widget.setCurrentIndex(0)
        self.tab_widget.setTabEnabled(1,False)
        self.tab_widget.setTabEnabled(2,False)
        self.client=Client()

class ConnectWidget(QtWidgets.QWidget):

    def __init__(self,parent_father):
        super(ConnectWidget,self).__init__()
        self.parent_father=parent_father
        self.btn_connect = QtWidgets.QPushButton('连接服务器',parent=self)
        self.btn_connect.setGeometry(QtCore.QRect(330, 220, 99, 28))

        self.label = QtWidgets.QLabel(text='请输入服务器ip和端口号',parent=self)
        self.label.setGeometry(QtCore.QRect(140, 180, 271, 20))

        font = QtGui.QFont()
        font.setBold(True)
        font.setFixedPitch(True)
        font.setWordSpacing(1)
        font.setPixelSize(13)

        self.lineEdit = QtWidgets.QLineEdit(parent=self)
        self.lineEdit.setGeometry(QtCore.QRect(140, 220, 171, 25))
        self.lineEdit.setInputMask('000. 000. 000. 000: 0000;0')
        # self.lineEdit.setFocusPolicy(0)
        # self.lineEdit.setFocusProxy(0)
        self.lineEdit.setTextMargins(3,2,3,2)
        self.lineEdit.setFont(font)
        self.lineEdit.setFocus()

        self.lineEdit.returnPressed.connect(self.connect_server)
        self.btn_connect.clicked.connect(self.connect_server)

    def connect_server(self):

        server_ip_port=self.lineEdit.text().replace(' ','')
        print(server_ip_port)

        req,server_allfile_paths,server_allfile_sizes=self.parent_father.client.check_server()
        if req:
            # 连接成功，页面启动
            self.parent_father.tab_widget.setTabEnabled(1,True)
            self.parent_father.tab_widget.setTabEnabled(2,True)
            self.parent_father.tab_widget.setCurrentIndex(1)
            # 初始化下载页面，获取服务器文件并更新窗口
            self.parent_father.downloadwidget.databasewidget.update_data(server_allfile_paths,server_allfile_sizes)
        else:
            self.parent_father.tab_widget.setTabEnabled(1,False)
            self.parent_father.tab_widget.setTabEnabled(2,False)

            QtWidgets.QMessageBox.warning(self,'警告','服务器连接错误，请检查ip和端口')
        pass

class DownloadWidget(QtWidgets.QWidget):
    def __init__(self,parent_father:QtWidgets.QMainWindow=None):
        super(DownloadWidget, self).__init__()
        self.setObjectName('downloadwidget')
        self.parent_father=parent_father
        self.databasewidget = DatabaseWidget(self, object_name='table_download_0', download_or_upload='下载')

        self.btn_download = QtWidgets.QPushButton(text='下载', parent=self)
        self.btn_download.setObjectName(u"btn_download_0")
        self.btn_download.setGeometry(QtCore.QRect(50, 480, 93, 28))
        self.btn_download.clicked.connect(self.ready_download)

        self.btn_exit = QtWidgets.QPushButton(text='退出', parent=self)
        self.btn_exit.setObjectName(u"btn_exit_0")

        self.btn_exit.setGeometry(QtCore.QRect(420, 480, 93, 28))
        self.btn_exit.clicked.connect(parent_father.close)

    @Slot()
    def ready_download(self):

        print('ready start download')
        index=self.databasewidget.table_database.selectedIndexes()
        # 下载途中不允许退出
        self.btn_exit.setEnabled(False)
        if len(index)==0:
            QtWidgets.QMessageBox.warning(self,'警告','请选择下载文件')
            pass

        elif len(index)==3:
            row=index[0].row()
            save_file_path,_=QtWidgets.QFileDialog.getSaveFileName(self,'保存文件')
            file_name=self.databasewidget.table_database.item(row,0).text()
            bar=self.databasewidget.table_database.cellWidget(row,2)
            thread=Thread(self,file_name,bar,save_file_path,download_or_upload='download')
            thread.start()
        else:
            #TODO 设置批量下载，保存到一个文件夹
            QtWidgets.QMessageBox.warning(self,'警告','每次只能同时选择一个文件下载')
            pass

class UpLoadWidget(QtWidgets.QWidget):

    def __init__(self,parent_father:QtWidgets.QMainWindow=None):
        super(UpLoadWidget, self).__init__()

        self.setObjectName('uploadwidget')
        self.parent_father=parent_father
        self.databasewidget = DatabaseWidget(self,object_name='table_upload_0', download_or_upload='上传')
        self.databasewidget.update_data([r'C:\Users\Lenovo\Desktop\photo\arknight\0.jpg',
                          r'C:\Users\Lenovo\Desktop\photo\arknight\20211203_140134.jpg'])

        self.btn_choosefile = QtWidgets.QPushButton(text='选择文件', parent=self)
        self.btn_choosefile.setObjectName(u"btn_choosefile_0")
        self.btn_choosefile.setGeometry(QtCore.QRect(50, 480, 93, 28))
        self.btn_choosefile.clicked.connect(self.choose_file)

        self.btn_upload=QtWidgets.QPushButton('开始上传',parent=self)
        self.btn_upload.setObjectName(u'btn_upload_0')
        self.btn_upload.setGeometry(QtCore.QRect(230, 480, 93, 28))
        self.btn_upload.clicked.connect(self.ready_upload)

        self.btn_del = QtWidgets.QPushButton(text='删除', parent=self)
        self.btn_del.setObjectName(u"btn_del_0")
        self.btn_del.setGeometry(QtCore.QRect(420, 480, 93, 28))
        self.btn_del.clicked.connect(self.databasewidget.remove_data)

    def ready_upload(self):
        # 准备上传文件的路径,开启多个线程
        index = self.databasewidget.table_database.selectedIndexes()
        #TODO 根据是否正在上传来选择是否可以删除，目前只能开始上传前进行删除
        #TODO 上传过程中进行暂停操作
        if len(index)==0:
            QtWidgets.QMessageBox.warning(self,'警告','请点击需要上传的文件')
            pass
        else:
            # self.btn_del.setEnabled(False)
            # 选取第文件路径
            for i in index[1::3]:
                row=i.row()
                file_path = self.databasewidget.table_database.item(row, 1).text()

                bar = self.databasewidget.table_database.cellWidget(row, 2)
                thread = Thread(parent_father=self,file_path=file_path,bar=bar,download_or_upload='upload')
                thread.start()

    def choose_file(self):
        # 选择文件
        filename_paths,_=QtWidgets.QFileDialog.getOpenFileNames(self)
        self.databasewidget.update_data(filename_paths)

class DatabaseWidget(object):
    def __init__(self,parent_father:QtWidgets.QWidget=None,object_name=None,download_or_upload='下载'):
        super(DatabaseWidget, self).__init__()
        self.parent_father=parent_father
        self.table_database = QtWidgets.QTableWidget(parent_father)
        self.table_database.setGeometry(QtCore.QRect(50, 20, 461, 451))
        self.table_database.setObjectName(object_name)
        self.table_database.setColumnCount(3)
        self.table_database.horizontalHeader().setStretchLastSection(True)

        self.table_database.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table_database.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table_database.setShowGrid(True)
        self.table_database.setGridStyle(Qt.NoPen)
        self.table_database.setWordWrap(True)
        self.table_database.setCornerButtonEnabled(True)
        self.table_database.setFixedSize(self.table_database.size())

        self.table_database.setFocusPolicy(Qt.NoFocus)

        self.table_database.horizontalHeader().setMinimumSectionSize(100)
        self.table_database.horizontalHeader().setMaximumSectionSize(300)
        self.table_database.horizontalHeader().setStretchLastSection(True)
        # self.table_database.verticalHeader().setVisible(False)
        self.table_database.verticalHeader().setMinimumSectionSize(20)
        self.table_database.verticalHeader().setMaximumSectionSize(30)
        self.table_database.verticalHeader().setDefaultSectionSize(25)
        self.font = QtGui.QFont()
        self.font.setFamilies([u"\u5fae\u8f6f\u96c5\u9ed1 Light"])
        self.font.setBold(True)

        tablewidget_item0 = QtWidgets.QTableWidgetItem()
        tablewidget_item0.setTextAlignment(Qt.AlignCenter)

        tablewidget_item0.setText('文件名')
        tablewidget_item0.setFont(self.font)
        self.table_database.setHorizontalHeaderItem(0, tablewidget_item0)

        tablewidget_item1 = QtWidgets.QTableWidgetItem()
        tablewidget_item1.setTextAlignment(Qt.AlignCenter)
        if download_or_upload=='下载':
            tablewidget_item1.setText('文件大小')
        else:
            tablewidget_item1.setText('文件路径')
        tablewidget_item1.setFont(self.font)
        self.table_database.setHorizontalHeaderItem(1, tablewidget_item1)

        tablewidget_item2 = QtWidgets.QTableWidgetItem()
        tablewidget_item2.setTextAlignment(Qt.AlignCenter)
        tablewidget_item2.setText(download_or_upload+'进度')
        tablewidget_item2.setFont(self.font)
        self.table_database.setHorizontalHeaderItem(2, tablewidget_item2)

    def update_data(self,filename_paths,file_sizes=None):
        '''
        :param data:[name_path1,name_path2 ]
            主进程可选择多个文件上传，但是上传后要显示在download中页面需要子进程 update one data
        :return:
        '''
        for i,pth in enumerate(filename_paths):

            items_list = self.parent_father.databasewidget.table_database.findItems(pth, Qt.MatchFlag.MatchExactly)
            if file_sizes!=None:
                self.update_onedata(pth,file_sizes[i])
            else:
                self.update_onedata(pth)
    @Slot(str)
    def update_onedata(self,pth,file_size=None):
        items_list = self.parent_father.databasewidget.table_database.findItems(os.path.basename(pth), Qt.MatchFlag.MatchExactly)
        if len(items_list) != 0:
            box = QtWidgets.QMessageBox.warning(self.parent_father,'警告','文件名重复，是否覆盖文件',QtWidgets.QMessageBox.Save|QtWidgets.QMessageBox.Cancel,
                               QtWidgets.QMessageBox.Save)
            if box.Save:
                # 确定重复名称覆盖
                self.parent_father.databasewidget.table_database.removeRow(items_list[0].row())
            else:
                return
        last_row = self.table_database.rowCount()
        btn_progressbar = QtWidgets.QProgressBar()
        btn_progressbar.setMaximum(99)
        btn_progressbar.setValue(0)
        name = os.path.basename(pth)
        self.table_database.insertRow(last_row)
        self.table_database.setItem(last_row, 0, QtWidgets.QTableWidgetItem(name))
        if file_size!=None:
            self.table_database.setItem(last_row, 1, QtWidgets.QTableWidgetItem(file_size))
        else:
            self.table_database.setItem(last_row, 1, QtWidgets.QTableWidgetItem(pth))
        self.table_database.setCellWidget(last_row, 2, btn_progressbar)

    def remove_data(self):
        '''
            删除选中的行
        '''
        index=self.table_database.selectedIndexes()
        if len(index)==0:
            QtWidgets.QMessageBox.warning(self.parent_father, "警告", "请先选择一行再进行操作")
            return
        index.sort(key=lambda x:x.row(),reverse=True)
        for i in index[::3]:
            self.table_database.removeRow(i.row())
        return

class Thread(QtCore.QThread):
    signal_progressbar=QtCore.Signal(int)
    signal_databasewidget_update=QtCore.Signal(str,str)
    def __init__(self,parent_father:QtWidgets.QWidget=None,file_path=None,bar=None,save_file_path=None,download_or_upload='download',debug_time_gap=0.1):
        QtCore.QThread.__init__(self,parent_father)
        self.parent_father=parent_father
        self.save_file_path=save_file_path
        # 对于下载操作这是文件名，上传操作这是文件路径
        self.file_path=file_path
        self.bar=bar
        self.download_or_upload=download_or_upload
        self.time_gap=debug_time_gap
        self.signal_progressbar.connect(self.update_bar)

        self.signal_databasewidget_update.connect(self.parent_father.parent_father.downloadwidget.databasewidget.update_onedata)

    @Slot(int)
    def update_bar(self, value):
        self.bar.setValue(value)

    def run(self):
        '''
        启动下载
        :return:
        '''
        if self.download_or_upload=='download':
            self.signal_progressbar.emit(0)
            self.parent_father.parent_father.client.download(self.file_path,self.signal_progressbar,self.save_file_path)
        if self.download_or_upload == 'upload':
            self.signal_progressbar.emit(0)
            self.parent_father.parent_father.client.upload(self.file_path,self.signal_progressbar)
            self.signal_databasewidget_update.emit(self.file_path,transfer_size(os.stat(self.file_path).st_size))

if __name__=='__main__':
    app = QtWidgets.QApplication(sys.argv)

    window=Main_Window()
    window.show()
    sys.exit(app.exec())