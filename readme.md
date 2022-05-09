## 使用步骤

#### clone 仓库

```bash
git clone https://github.com/dummerchen/FileTransferSystem.git
cd FileTransferSystem
```

#### 运行服务端

可以增加服务端文件夹参数

* root_dir:  -rd 服务器默认文件夹路径 ，默认 './download'
* ip_port : -ip 服务器启动ip和端口号，默认 '127.0.0.1:9393'

```bash
mkdir Download
python server.py -rd ./Download -ip 127.0.0.1:9393
```



#### 运行客户端

服务端启动后即可运行客户端。

```bash
python main.py
```

