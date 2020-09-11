# 对单个文件的操作
import os
import cryptotools

# 规定了所有文件文件名当中的内容,以及一些基本属性
class BasicFile(object):
    # 构造函数
    def __init__(self):
        # 包元素的整体
        self.unencrypted_fragment = {}              # 含有所有的包元素
        # 文件名中的内容
        self.sender_name = None                 # 发送方的名字或代号
        self.receiver_name = None               # 接收方的名字或代号
        self.cover_traffic = None               # 不是掩护流量为0,是掩护流量为1.掩护流量将不会被分析
        self.type_of_use = None                 # 用途.0为握手,1为传输数据,2为挥手
        self.file_name = None                   # 待发送文件的文件名
        self.full_data_length = None            # 本报文中的data在组合完全后的长度
        self.identification = None              # 标识.完整的报文的所有切片都具有统一的标识
        self.fragment_data_length = None        # 本切片的数据部分长度
        self.sn_of_fragment = None              # 本切片的编号
        self.more_fragment = None               # MF,是否还有分片位,1表示后面还有分片,0表示已经是最后分片
        self.timer = None                       # 计时器,超时会发送失败结果确认
        self.nonce = None                       # 12字节随机数,用于数据传输时的消息验证
        # 数据部分
        self.data = None                        # 数据部分(未加密)
        # 秘钥
        self.sender_public_key = None           # 发送方的公钥
        self.sender_private_key = None          # 发送方的私钥
        self.receiver_public_key = None         # 接收方的公钥
        self.receiver_private_key = None        # 接收方的私钥
        self.symmetric_key = None               # 用于加密数据的对称秘钥
        # 仓库地址
        self.repo_dir = None                    # 交流用的仓库的地址
        # 未加密和加密过的包文本
        self.unencrypted_fragment_header = None # 未加密的包头部
        self.encrypted_fragment_header = None   # 已加密的包头部
        self.unencrypted_fragment_data = None   # 未加密的包数据部分
        self.encrypted_fragment_data = None     # 已加密的包数据部分
        # 作为信息载体的已被加密的文件的路径
        self.encrypted_file_dir = None          # 已被加密文件的路径
        # ECDH出的对称秘钥
        self.shared_key = None                  # ECDH出的32字节秘钥


# 发送方对握手文件进行的处理,目的是生成握手文件
class ShakeHandFileEncoder(BasicFile):
    # 构造函数
    def __init__(self, unencrypted_fragment):
        self.unencrypted_fragment = unencrypted_fragment
        self.sender_name = self.unencrypted_fragment['sender_name']
        self.receiver_name = self.unencrypted_fragment['receiver_name']
        self.type_of_use = self.unencrypted_fragment['type_of_use']
        self.full_data_length = self.unencrypted_fragment['full_data_length']

    # 生成握手用的pem文件
    def GenerateShakeHandFile(self):
        pass


# 接收方对握手文件进行的处理,目的是ECDH出对称密钥
class ShakeHandFileDecoder(BasicFile):
    # 构造函数
    def __init__(self):
        pass

    # 解读
    def DecodeShakeHandFile(self):
        pass


# 对单个文件的加密处理
class DataFileEncoder(BasicFile):
    # 构造函数
    def __init__(self, unencrypted_fragment, repo_dir, receiver_public_key, shared_key):
        # 从基类引入基础属性
        super(DataFileEncoder, self).__init__()
        # 密钥
        self.receiver_public_key = receiver_public_key
        self.shared_key = shared_key
        # 仓库地址
        self.repo_dir = repo_dir
        # 获得包头部元素
        self.unencrypted_fragment = unencrypted_fragment
        self.sender_name = self.unencrypted_fragment['sender_name']
        self.receiver_name = self.unencrypted_fragment['receiver_name']
        self.cover_traffic = self.unencrypted_fragment['cover_traffic']
        self.type_of_use = self.unencrypted_fragment['type_of_use']
        self.file_name = self.unencrypted_fragment['file_name']
        self.full_data_length = self.unencrypted_fragment['full_data_length']
        self.identification = self.unencrypted_fragment['identification']
        self.fragment_data_length = self.unencrypted_fragment['fragment_data_length']
        self.sn_of_fragment = self.unencrypted_fragment['sn_of_fragment']
        self.more_fragment = self.unencrypted_fragment['more_fragment']
        self.timer = self.unencrypted_fragment['timer']
        self.nonce = bytes(self.unencrypted_fragment['nonce'], encoding="ascii")
        # 获得包数据部分
        self.data = self.unencrypted_fragment['data']
        # 获得加密的头部和数据
        self.unencrypted_fragment_header = " ".join([str(i) for i in list(unencrypted_fragment.values())[0:-1]])  # 将头部元素压缩成字符串
        self.unencrypted_fragment_data = self.data

    # 获取未加密的头部(文件名)字符串
    def GetUnencryptedFragmentHeader(self):
        return self.unencrypted_fragment_header

    # 获取未加密的数据部分
    def GetUnencryptedFragmentData(self):
        return self.unencrypted_fragment_data

    # 获取加密的头部(文件名)字符串
    def GetEncryptedFragmentHeader(self):
        return self.encrypted_fragment_header

    # 获取加密的数据部分
    def GetEncryptedFragmentData(self):
        return self.encrypted_fragment_data

    # 加密文件,并设定加密的文件的目录.注意这里的目录是相对于仓库的目录
    def GenerateEncryptedFile(self):
        self.encrypted_fragment_header = cryptotools.RSAEncodeData(self.unencrypted_fragment_header, self.receiver_public_key)
        chacha = cryptotools.CC20P1305Init(self.shared_key)
        self.encrypted_fragment_data = cryptotools.CC20P1305Encrypt(chacha, self.nonce, self.unencrypted_fragment_data)
        self.encrypted_file_dir = self.repo_dir + "/" + self.encrypted_fragment_header
        with open(self.encrypted_file_dir, 'wb') as f:
            f.write(self.encrypted_fragment_data)

    # 获取加密的文件的目录
    def GetEncryptedFileDir(self):
        return self.encrypted_file_dir


# 对单个文件的解密处理
class DataFileDecoder(BasicFile):
    # 构造函数
    def __init__(self, encrypted_file_dir, receiver_private_key, shared_key):
        # 从基类引入基础属性
        super(DataFileDecoder, self).__init__()
        # 秘钥和文件地址
        self.encrypted_file_dir = encrypted_file_dir
        self.receiver_private_key = receiver_private_key
        self.shared_key = shared_key
        # 解析未加密的文件名和文件数据
        self.encrypted_fragment_header = os.path.splitext(os.path.split(encrypted_file_dir)[1])[0]  # 从文件路径当中提取出不带后缀的文件名
        self.unencrypted_fragment_header = cryptotools.RSADecodeData(self.encrypted_fragment_header, receiver_private_key).decode('utf-8')
        # 解析出包中应该包含的元素,用来之后打包和判断是不是合法
        unencrypted_fragment_header_list = self.unencrypted_fragment_header.split(" ")
        self.sender_name = unencrypted_fragment_header_list[0]
        self.receiver_name = unencrypted_fragment_header_list[1]
        self.cover_traffic = int(unencrypted_fragment_header_list[2])
        self.type_of_use = int(unencrypted_fragment_header_list[3])
        self.file_name = unencrypted_fragment_header_list[4]
        self.full_data_length = int(unencrypted_fragment_header_list[5])
        self.identification = unencrypted_fragment_header_list[6]
        self.fragment_data_length = int(unencrypted_fragment_header_list[7])
        self.sn_of_fragment = int(unencrypted_fragment_header_list[8])
        self.more_fragment = int(unencrypted_fragment_header_list[9])
        self.timer = int(unencrypted_fragment_header_list[10])
        self.nonce = bytes(unencrypted_fragment_header_list[11], encoding="ascii")

    # 根据文件名检查发送方和接收方的名称,以及是不是掩护流量,决定这个文件是继续分析还是丢弃
    def CheckNameAndCoverTraffic(self, sender_name, receiver_name):
        if self.sender_name == sender_name and self.receiver_name == receiver_name:
            if self.cover_traffic == 0:
                return True
        return False

    # 获得共享的对称密钥
    def GenerateECDHSharedKey(self):
        with open(self.encrypted_file_dir, 'rb') as f:
            self.encrypted_fragment_data = f.read()
        self.unencrypted_fragment_data = cryptotools.RSADecodeData(self.encrypted_fragment_header, self.receiver_private_key).decode('utf-8')
        print(self.unencrypted_fragment_data)

    # 解密一个文件并拆出里面的元素
    def GenerateDataFragmentList(self):
        with open(self.encrypted_file_dir, 'rb') as f:
            self.encrypted_fragment_data = f.read()
        chacha = cryptotools.CC20P1305Init(self.shared_key)
        self.unencrypted_fragment_data = cryptotools.CC20P1305Decrypt(chacha, self.nonce, self.encrypted_fragment_data)
        self.data = self.unencrypted_fragment_data
        # 打包
        self.unencrypted_fragment['sender_name'] = self.sender_name
        self.unencrypted_fragment['receiver_name'] = self.receiver_name
        self.unencrypted_fragment['cover_traffic'] = self.cover_traffic
        self.unencrypted_fragment['type_of_use'] = self.type_of_use
        self.unencrypted_fragment['file_name'] = self.file_name
        self.unencrypted_fragment['full_data_length'] = self.full_data_length
        self.unencrypted_fragment['identification'] = self.identification
        self.unencrypted_fragment['fragment_data_length'] = self.fragment_data_length
        self.unencrypted_fragment['sn_of_fragment'] = self.sn_of_fragment
        self.unencrypted_fragment['more_fragment'] = self.more_fragment
        self.unencrypted_fragment['data'] = self.data
        self.unencrypted_fragment['file_dir'] = self.encrypted_file_dir
        self.unencrypted_fragment['timer'] = self.timer
        self.unencrypted_fragment['nonce'] = self.nonce

    # 获得各个数据元素
    def GetDataFragmentList(self):
        return self.unencrypted_fragment

    # 获取文件的类型
    def GetTypeOfUse(self):
        return self.type_of_use
