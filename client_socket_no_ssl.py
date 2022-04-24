import socket
import time,os,struct,json

class Client():
    def __init__(self,server_ip_port='127.0.0.1:9393'):

        # 与服务端建立socket连接

        self.server_ip_port =server_ip_port
        self.ip = server_ip_port[:-5]
        self.port = int(server_ip_port[-4:])
        self.req = False

    def check_server(self):
        try:
            # 与服务器进行连接
            self.ssock = socket.create_connection((self.ip,self.port))
            # 定义文件头信息，包含文件名和文件大小
            header = {
                'Command': 'Check',
                'filename': '',
                'filesize': '',
                'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            }
            header_hex = bytes(json.dumps(header).encode('utf-8'))
            fhead = struct.pack('1024s', header_hex)
            self.ssock.send(fhead)

            fileinfo_size = struct.calcsize('128s')

            buf = self.ssock.recv(fileinfo_size)

            header_json = str(struct.unpack('128s', buf)[0], encoding='utf-8').strip('\00')
            header = json.loads(header_json)
            stat = header['stat']
            fileSize=header['filesize']
            if stat=='Success':
                print('Client Check Success')
                recvd_size=0
                allfile_pths=[]
                # tempinfo = struct.calcsize('1024s')

                while not recvd_size == fileSize:
                    temp = self.ssock.recv(1024)
                    recvd_size += 1
                    path=json.loads(str(struct.unpack('1024s',temp)[0],encoding='utf-8').strip('\00'))
                    allfile_pths.append(path['path'])

                return True,allfile_pths
            return False,[]
        except Exception as e:
            print(e)
            return False,e

    def upload(self,file_path,singal_progressbar):
        try:
            # 定义文件头信息，包含文件名和文件大小
            # ssock = socket.create_connection((self.ip, self.port))
            file_size=os.stat(file_path).st_size
            file_name=os.path.basename(file_path)
            header = {
                'Command': 'Upload',
                'file_name': file_name,
                'file_size': file_size,
            }
            header_hex = bytes(json.dumps(header).encode('utf-8'))
            fhead = struct.pack('1024s', header_hex)
            print('client',header)
            self.ssock.send(fhead)

            fo = open(file_path, 'rb')
            already_uploadsize=0
            while True:
                filedata = fo.read(1024)
                if not filedata:
                    break
                self.ssock.send(filedata)
                already_uploadsize+=len(filedata)
                singal_progressbar.emit(already_uploadsize/file_size*100)
            fo.close()
            # self.ssock.close()
        except Exception as e:
            print(e)
            return False

    def download(self, file_path ,singal_progressbar,save_file_path):
        # 定义文件头信息，包含文件名和文件大小
        header = {
            'Command': 'Download',
            'file_path': file_path,
            'file_size': '',
        }
        header_hex = bytes(json.dumps(header).encode('utf-8'))
        fhead = struct.pack('1024s', header_hex)
        self.ssock.send(fhead)

        fileinfo_size = struct.calcsize('128s')
        buf = self.ssock.recv(fileinfo_size)
        if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
            header_json = str(struct.unpack('128s', buf)[0], encoding='utf-8').strip('\00')
            print(header_json)
            header = json.loads(header_json)
            stat = header['stat']
            if stat == 'Success':
                fileSize = header['file_size']

                recvd_size = 0  # 定义接收了的文件大小
                file = open(save_file_path, 'wb')

                while not recvd_size == fileSize:
                    if fileSize - recvd_size > 1024:
                        rdata = self.ssock.recv(1024)
                        recvd_size += len(rdata)
                    else:
                        rdata = self.ssock.recv(fileSize - recvd_size)
                        recvd_size = fileSize
                    singal_progressbar.emit(recvd_size/fileSize*100)
                    file.write(rdata)
                file.close()
                return True
            else:
                return False

if __name__ == "__main__":
    client = Client()
