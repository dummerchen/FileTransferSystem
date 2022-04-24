import socket
import threading, struct, json, os, pymysql
from glob import glob
from argparse import ArgumentParser
class Server():
    def __init__(self,server_ip_port,server_default_path=r'C:\Users\Public'):
        self.server_ip_port = server_ip_port
        self.server_default_path = server_default_path
        self.ip = server_ip_port[:-5]
        self.port = int(server_ip_port[-4:])
        self.req=False

    def listen(self):
        # 监听端口
        print('server start')
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0) as ssock:
            ssock.bind((self.ip,self.port))
            ssock.listen(5)

            while True:
                # 接收客户端连接
                connection, addr = ssock.accept()
                print('Connected by ', addr)
                #开启多线程,这里arg后面一定要跟逗号，否则报错
                thread = threading.Thread(target=self.conn_thread, args=(connection,))
                thread.start()

    def conn_thread(self,connection):
        while True:
            try:
                connection.settimeout(60)
                fileinfo_size = struct.calcsize('1024s')
                buf = connection.recv(fileinfo_size)
                if buf:  # 如果不加这个if，第一个文件传输完成后会自动走到下一句
                    header_json = str(struct.unpack('1024s', buf)[0], encoding='utf-8').strip('\00')
                    print(header_json)
                    header = json.loads(header_json)
                    Command = header['Command']

                    if Command=='Check':

                        filepaths = glob(self.server_default_path + '/*.*')
                        header = {
                            'Feedback': 'Check',
                            'filesize': len(filepaths),
                            'stat': 'Success',
                        }
                        header_hex = bytes(json.dumps(header).encode('utf-8'))
                        fhead = struct.pack('128s', header_hex)

                        connection.send(fhead)

                        for pth in filepaths:
                            byte=struct.pack('1024s', bytes(json.dumps({'path':pth,'size':os.stat(pth).st_size}).encode('utf-8')))
                            connection.send(byte)

                        print('server check over...')

                    if Command == 'Upload' :
                        file_name = header['file_name']
                        file_size = header['file_size']
                        filenewname = os.path.join(self.server_default_path, file_name)

                        recvd_size = 0  # 定义接收了的文件大小
                        file = open(filenewname, 'wb')
                        while not recvd_size == file_size:
                            if file_size - recvd_size > 1024:
                                rdata = connection.recv(1024)
                                recvd_size += len(rdata)
                            else:
                                rdata = connection.recv(file_size - recvd_size)
                                recvd_size = file_size
                            file.write(rdata)
                        file.close()

                    if Command == 'Download':
                        # 查询数据表数据
                        file_name=header['file_path']
                        # 定义文件头信息，包含文件名和文件大小
                        file_path=os.path.join(self.server_default_path,file_name)
                        header = {
                            'Feedback': Command,
                            'stat': 'Success',
                            'file_size': os.stat(file_path).st_size,
                        }
                        header_hex = bytes(json.dumps(header).encode('utf-8'))
                        fhead = struct.pack('128s', header_hex)
                        connection.send(fhead)

                        fo = open(file_path, 'rb')
                        while True:
                            filedata = fo.read(1024)
                            if not filedata:
                                break
                            connection.send(filedata)
                        fo.close()

            except socket.timeout:
                connection.close()
                break
            except ConnectionResetError:
                connection.close()
                break

if __name__ == "__main__":
    args=ArgumentParser()
    args.add_argument('--root_dir','-rd',default=r'C:\Users\Public')
    args.add_argument('--ip_port','-ip',default=r'127.0.0.1:9393')
    opts=args.parse_args()
    server=Server(opts.ip_port,opts.root_dir)
    server.listen()