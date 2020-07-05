# 对单个文件的操作
import functiontimer
import os
import cryptotools


# 握手文件的的属性和基本方法
class ShakeHandFile(object):
    # 构造函数
    def __init__(self):
        # 包的通用组成元素
        self.sender_name = ""               # 发送方的名字或代号
        self.receiver_name = ""             # 接收方的名字或代号
        self.type_of_use = -1               # 本报文用途.0为传输数据,1为发起握手,2为回应握手,3为发起挥手,4为响应挥手
        self.full_data_length = -1          # 本报文中的data在组合完全后的长度
        # 作为握手包的已被加密的文件的路径
        self.encrypted_file_dir = ""        # 已被加密文件的路径


# 发送方对握手文件进行的处理,目的是生成握手文件
class ShakeHandFileEncoder(ShakeHandFile):
    # 构造函数
    def __init__(self, packet_element):
        self.packet_element = packet_element
        self.sender_name = self.packet_element['sender_name']
        self.receiver_name = self.packet_element['receiver_name']
        self.type_of_use = self.packet_element['type_of_use']
        self.full_data_length = self.packet_element['full_data_length']

    # 生成握手用的pem文件
    def GenerateShakeHandFile(self):
        pass


# 接收方对握手文件进行的处理,目的是ECDH出对称密钥
class ShakeHandFileDecoder(ShakeHandFile):
    # 构造函数
    def __init__(self):
        pass

    # 解读
    def DecodeShakeHandFile(self):
        pass


# 数据文件的的属性和基本方法
class DataFile(object):
    # 构造函数
    def __init__(self):
        # 包元素的整体
        self.packet_element = {}            # 含有所有的包元素
        # 包的通用组成元素
        self.sender_name = ""               # 发送方的名字或代号
        self.receiver_name = ""             # 接收方的名字或代号
        self.cover_traffic = -1             # 不是掩护流量为0,是掩护流量为1.掩护流量将不会被分析
        self.type_of_use = -1               # 本报文用途.0为传输数据,1为发起握手,2为回应握手,3为发起挥手,4为响应挥手
        self.full_data_length = -1          # 本报文中的data在组合完全后的长度
        self.identification = -1            # 标识.完整的报文的所有切片都具有统一的标识
        self.fragment_data_length = -1      # 本切片的数据部分长度
        self.sn_of_fragment = -1            # 本切片的编号
        self.more_fragment = -1             # MF,是否还有分片位,1表示后面还有分片,0表示已经是最后分片
        self.nonce = b""                    # 12字节随机数,用于数据传输时的消息验证
        self.data = ""                      # 数据部分(未加密)
        # 秘钥
        self.sender_public_key = ""         # 发送方的公钥
        self.sender_private_key = ""        # 发送方的私钥
        self.receiver_public_key = ""       # 接收方的公钥
        self.receiver_private_key = ""      # 接收方的私钥
        self.symmetric_key = ""             # 用于加密数据的对称秘钥
        # 仓库地址
        self.repo_dir = ""                  # 交流用的仓库的地址
        # 未加密和加密过的包文本
        self.unencrypted_packet_header = "" # 未加密的包头部
        self.encrypted_packet_header = ""   # 已加密的包头部
        self.unencrypted_packet_data = ""   # 未加密的包数据部分
        self.encrypted_packet_data = ""     # 已加密的包数据部分
        # 作为信息载体的已被加密的文件的路径
        self.encrypted_file_dir = ""        # 已被加密文件的路径
        # ECDH出的对称秘钥
        self.shared_key = b''               # ECDH出的32字节秘钥

    # 打印整个数据包
    def PrintPacketInfo(self, print_all=True):
        if print_all:
            print(dict(list(self.__dict__.items())[0:-1]))
        else:
            print(dict(list(self.__dict__.items())))

    # 验证完整性
    def CheckIntegrity(self):
        pass


# 对"单个"数据分片加上头部后加密,使之变成一个数据包,随后隐写入文件
class DataFileEncoder(DataFile):
    # 构造函数
    def __init__(self, packet_element, receiver_public_key):
        # 从基类引入基础属性
        super(DataFileEncoder, self).__init__()
        # 加密头部的秘钥
        self.receiver_public_key = receiver_public_key
        # 获得包头部元素
        self.packet_element = packet_element
        self.sender_name = self.packet_element['sender_name']
        self.receiver_name = self.packet_element['receiver_name']
        self.cover_traffic = self.packet_element['cover_traffic']
        self.full_data_length = self.packet_element['full_data_length']
        self.identification = self.packet_element['identification']
        self.fragment_data_length = self.packet_element['fragment_data_length']
        self.sn_of_fragment = self.packet_element['sn_of_fragment']
        self.more_fragment = self.packet_element['more_fragment']
        self.nonce = bytes(self.packet_element['nonce'], encoding="ascii")
        # 获得包数据部分
        self.data = self.packet_element['data']
        # 仓库地址
        self.repo_dir = self.packet_element['repo_dir']
        # 获得对称秘钥
        self.shared_key = self.packet_element['shared_key']
        # 获得加密的头部和数据
        self.unencrypted_packet_header = " ".join([str(i) for i in list(packet_element.values())[0:-3]])  # 将头部元素压缩成字符串
        self.unencrypted_packet_data = self.data

    # 获取未加密的头部(文件名)字符串
    def GetUnencryptedPacketHeader(self):
        return self.unencrypted_packet_header

    # 获取未加密的数据部分
    def GetUnencryptedPacketData(self):
        return self.unencrypted_packet_data

    # 获取加密的头部(文件名)字符串
    def GetEncryptedPacketHeader(self):
        return self.encrypted_packet_header

    # 获取加密的数据部分
    def GetEncryptedPacketData(self):
        return self.encrypted_packet_data

    # 加密文件,并设定加密的文件的目录.注意这里的目录是相对于仓库的目录
    def GenerateEncryptedFile(self):
        self.encrypted_packet_header = cryptotools.RSAEncodeData(self.unencrypted_packet_header, self.receiver_public_key)
        chacha = cryptotools.CC20P1305Init(self.shared_key)
        self.encrypted_packet_data = cryptotools.CC20P1305Encrypt(chacha, self.nonce, self.unencrypted_packet_data)
        self.encrypted_file_dir = self.repo_dir + "/" + self.encrypted_packet_header
        with open(self.encrypted_file_dir, 'wb') as f:
            f.write(self.encrypted_packet_data)

    # 获取加密的文件的目录
    def GetEncryptedFileDir(self):
        return self.encrypted_file_dir


# 对"单个"数据包的解隐写和解密处理
class DataFileDecoder(DataFile):
    # 构造函数
    def __init__(self, encrypted_file_dir, receiver_private_key, shared_key):
        # 从基类引入基础属性
        super(DataFileDecoder, self).__init__()
        # 秘钥和文件地址
        self.encrypted_file_dir = encrypted_file_dir
        self.receiver_private_key = receiver_private_key
        self.shared_key = shared_key
        # 解析未加密的文件名和文件数据
        self.encrypted_packet_header = os.path.splitext(os.path.split(encrypted_file_dir)[1])[0]  # 从文件路径当中提取出不带后缀的文件名
        self.unencrypted_packet_header = cryptotools.RSADecodeData(self.encrypted_packet_header, receiver_private_key).decode('utf-8')
        # 解析出包中应该包含的元素,用来之后打包和判断是不是合法
        unencrypted_packet_header_list = self.unencrypted_packet_header.split(" ")
        self.sender_name = unencrypted_packet_header_list[0]
        self.receiver_name = unencrypted_packet_header_list[1]
        self.cover_traffic = int(unencrypted_packet_header_list[2])
        self.full_data_length = int(unencrypted_packet_header_list[3])
        self.identification = int(unencrypted_packet_header_list[4])
        self.fragment_data_length = int(unencrypted_packet_header_list[5])
        self.sn_of_fragment = int(unencrypted_packet_header_list[6])
        self.more_fragment = int(unencrypted_packet_header_list[7])
        self.nonce = bytes(unencrypted_packet_header_list[8], encoding="ascii")

    # 根据文件名检查发送方和接收方的名称,以及是不是掩护流量,决定这个文件是继续分析还是丢弃
    def CheckNameAndCoverTraffic(self, sender_name, receiver_name):
        if self.sender_name == sender_name and self.receiver_name == receiver_name:
            if self.cover_traffic == 0:
                return True
        return False

    # 生成包含各个元素的数据包
    def GeneratePacketElement(self):
        with open(self.encrypted_file_dir, 'rb') as f:
            self.encrypted_packet_data = f.read()
        chacha = cryptotools.CC20P1305Init(self.shared_key)
        self.unencrypted_packet_data = cryptotools.CC20P1305Decrypt(chacha, self.nonce, self.encrypted_packet_data)
        self.data = self.unencrypted_packet_data
        # 打包
        self.packet_element['sender_name'] = self.sender_name
        self.packet_element['receiver_name'] = self.receiver_name
        self.packet_element['cover_traffic'] = self.cover_traffic
        self.packet_element['full_data_length'] = self.full_data_length
        self.packet_element['identification'] = self.identification
        self.packet_element['fragment_data_length'] = self.fragment_data_length
        self.packet_element['sn_of_fragment'] = self.sn_of_fragment
        self.packet_element['more_fragment'] = self.more_fragment
        self.packet_element['data'] = self.data
        self.packet_element['file_dir'] = self.encrypted_file_dir
        self.packet_element['nonce'] = self.nonce

    # 获得各个数据元素
    def GetPacketElement(self):
        return self.packet_element
