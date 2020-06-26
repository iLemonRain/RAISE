# 对单个文件的操作
import os
import cryptotools

# 数据包的属性和基本方法
class Packet(object):
    # 构造函数
    def __init__(self):
        # 包元素的整体
        self.packet_element = {}             # 含有所有的包元素
        # 包的组成元素
        self.sender_name = ""                # 发送方的名字或代号
        self.receiver_name = ""              # 接收方的名字或代号
        self.cover_traffic = -1              # 不是掩护流量为0,是掩护流量为1.掩护流量将不会被分析
        # self.type_of_use = -1              # 本报文用途.0为传输数据,1为发起握手,2为回应握手
        self.full_data_length = -1           # 本报文中的data在组合完全后的长度
        self.identification = -1             # 标识.完整的报文的所有切片都具有统一的标识
        self.fragment_data_length = -1       # 本切片的数据部分长度
        self.sn_of_fragment = -1             # 本切片的编号
        self.more_fragment = -1              # MF,是否还有分片位,1表示后面还有分片,0表示已经是最后分片
        self.data = ""                       # 数据部分(未加密)
        # 秘钥
        self.sender_public_key = ""          # 发送方的公钥
        self.sender_private_key = ""         # 发送方的私钥
        self.receiver_public_key = ""        # 接收方的公钥
        self.receiver_private_key = ""       # 接收方的私钥
        self.symmetric_key = ""              # 用于加密数据的对称秘钥
        # 仓库地址
        self.repo_dir = ""                   # 交流用的仓库的地址
        # 未加密和加密过的包文本
        self.unencrypted_packet_header = ""  # 未加密的包头部
        self.encrypted_packet_header = ""    # 已加密的包头部
        self.unencrypted_packet_data = ""    # 未加密的包数据部分
        self.encrypted_packet_data = ""      # 已加密的包数据部分
        # 作为信息载体的未加密的文件和已被加密的文件的路径
        self.unencrypted_file = ""           # 未被加密的文件
        self.unencrypted_file_dir = ""       # 未被加密文件的路径
        self.encrypted_file = ""             # 已被加密的文件
        self.encrypted_file_dir = ""         # 已被加密文件的路径

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
    def __init__(self, packet_element, receiver_public_key):
        # 从基类引入基础属性
        super(FileEncoder, self).__init__()
        # 秘钥
        self.receiver_public_key = receiver_public_key
        # 获得包元素整体
        self.packet_element = packet_element
        # 解析出包的组成元素
        self.sender_name = self.packet_element['sender_name']
        self.receiver_name = self.packet_element['receiver_name']
        self.cover_traffic = self.packet_element['cover_traffic']
        self.full_data_length = self.packet_element['full_data_length']
        self.identification = self.packet_element['identification']
        self.fragment_data_length = self.packet_element['fragment_data_length']
        self.sn_of_fragment = self.packet_element['sn_of_fragment']
        self.more_fragment = self.packet_element['more_fragment']
        self.data = self.packet_element['data']
        # 仓库地址
        self.repo_dir = self.packet_element['repo_dir']
        # 获得加密的头部和数据
        self.unencrypted_packet_header = " ".join([str(i) for i in list(packet_element.values())[0:-2]]) # 将头部元素压缩成字符串
        # self.unencrypted_packet_header = " ".join([str(i) for i in list(self.__dict__.values())[0:8]]) # 将头部元素压缩成字符串
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
class FileDecoder(Packet):
    # 构造函数
    def __init__(self, encrypted_file_dir, receiver_private_key):
        # 从基类引入基础属性
        super(FileDecoder, self).__init__()
        # 秘钥和文件地址
        self.receiver_private_key = receiver_private_key
        self.encrypted_file_dir = encrypted_file_dir
        # 解析未加密的文件名和文件数据
        self.encrypted_packet_header = os.path.splitext(os.path.split(encrypted_file_dir)[1])[0] # 从文件路径当中提取出不带后缀的文件名
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

    # 根据文件名检查发送方和接收方的名称,以及是不是掩护流量,决定这个文件是继续分析还是丢弃
    def CheckNameAndCoverTraffic(self, sender_name, receiver_name):
        if self.sender_name == sender_name and self.receiver_name == receiver_name:
            if self.cover_traffic == 0:
                return True
        return False

    # 生成包含各个元素的数据包
    def GeneratePacketElement(self):
        with open(self.encrypted_file_dir, 'r+') as f:
            self.encrypted_packet_data = f.read()
        self.unencrypted_packet_data = self.encrypted_packet_data # 目前还没有写数据的加密部分,以后补上
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
        print(self.packet_element)

    # 获得各个数据元素
    def GetPacketElement(self):
        return self.packet_element
