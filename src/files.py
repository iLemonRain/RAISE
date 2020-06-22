# 对单个文件的操作
import os
import cryptotools
from PIL import Image

# 数据包的属性和基本方法
class Packet(object):
    # 包的组成元素
    sender_name = ""                # 发送方的名字或代号
    receiver_name = ""              # 接收方的名字或代号
    cover_traffic = -1              # 不是掩护流量为0,是掩护流量为1.掩护流量将不会被分析
    # type_of_use = -1              # 本报文用途.0为传输数据,1为发起握手,2为回应握手
    full_data_length = -1           # 本报文中的data在组合完全后的长度
    identification = -1             # 标识.完整的报文的所有切片都具有统一的标识
    fragment_data_length = -1       # 本切片的塔塔部分长度
    sn_of_fragment = -1             # 本切片的编号
    more_fragment = -1              # MF,是否还有分片位,1表示后面还有分片,0表示已经是最后分片
    data = ""                       # 数据部分
    # 秘钥
    sender_private_key = ""         # 发送方的私钥
    receiver_public_key = ""        # 接收方的公钥
    symmetric_key = ""              # 用于加密数据的对称秘钥
    # 仓库地址
    repo_dir = ""                   # 交流用的仓库的地址
    # 未加密和加密过的包文本
    unencrypted_packet_header = ""  # 未加密的包头部
    encrypted_packet_header = ""    # 已加密的包头部
    unencrypted_packet_data = ""    # 未加密的包数据部分
    encrypted_packet_data = ""      # 已加密的包数据部分
    # 作为信息载体的未加密的文件和已被加密的文件的路径
    unencrypted_file = ""           # 未被加密的文件
    unencrypted_file_dir = ""       # 未被加密文件的路径
    encrypted_file = ""             # 已被加密的文件
    encrypted_file_dir = ""         # 已被加密文件的路径

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
class FileEncoder(Packet):
    # 构造函数
    def __init__(self, packet_element):
        # 包的组成元素
        self.sender_name = packet_element['sender_name']
        self.receiver_name = packet_element['receiver_name']
        self.cover_traffic = packet_element['cover_traffic']
        self.full_data_length = packet_element['full_data_length']
        self.identification = packet_element['identification']
        self.fragment_data_length = packet_element['fragment_data_length']
        self.sn_of_fragment = packet_element['sn_of_fragment']
        self.more_fragment = packet_element['more_fragment']
        self.data = packet_element['data']
        # 秘钥
        self.receiver_public_key = packet_element['receiver_public_key']
        # 仓库地址
        self.repo_dir = packet_element['repo_dir']
        # 获得加密的头部和数据
        self.unencrypted_packet_header = " ".join([str(i) for i in list(self.__dict__.values())[0:8]]) # 将头部元素压缩成字符串
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
        self.encrypted_packet_data = self.unencrypted_packet_data # 这里应该使用秘钥加密一下,现在还没有写
        self.encrypted_file_dir = self.repo_dir + "/" + self.encrypted_packet_header
        with open(self.encrypted_file_dir, 'w+') as f:
            f.write(self.encrypted_packet_data)

    # 获取加密的文件的目录
    def GetEncryptedFileDir(self):
        return self.encrypted_file_dir


# 对"单个"数据包的解隐写和解密处理
class FileDecoder(FileEncoder):
    # 将隐写的文件解包
    def UnwrapStegedFileProgress(self, encrypted_file):
        # packet = ""
        # ...
        # return packet
        pass

    # 将数据解密,返回解密的数据
    def DecryptProgress(self, private_key, data):
        # ...
        # return decrupted_data
        pass
