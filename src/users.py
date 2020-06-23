# 本脚本定义了发送方和接收方的整体操作.
# 对单个数据分片的操作,如数据包的编码解码过程,请见files.py
import os
import glob
import random
import string
import math
import cryptotools
import repotools


# peer的属性和基本方法(操作的是整个数据流)
class Peer(object):
    # 发送方和接收方的名字或代号
    sender_name = ""                # 发送方的名字或代号
    receiver_name = ""              # 接收方的名字或代号
    # 仓库对象
    repo = None                     # 仓库对象
    repo_dir = []                   # 仓库根目录
    # 自己和对方的秘钥对
    sender_public_key = ""          # 发送方的公钥位置
    sender_private_key = ""         # 发送方的私钥位置
    receiver_public_key = ""        # 接收方的公钥位置
    receiver_private_key = ""       # 接受方的私钥位置
    # 和文件存储位置相关
    unencrypted_file_dir_list = []  # 存放所有未被加密的文件的位置列表
    encrypted_file_dir_list = []    # 存放所有已被加密的文件的位置列表
    # 和传输的文本数据相关
    fragment_data_length = -1       # 每个分片中数据的长度
    plain_data = ""                 # 未加密的整段文本
    plain_data_fragment_list = []   # 未加密的数据分片的列表(包含数据分片和掩护流量分片)
    # 和传输的所有数据包的构成有关
    packet_element_list = []        # 所有经过发送方或者接收方处理(添加/忽略掩护流量分片)后的包元素列表

    # 设置发送方的姓名或代号
    def SetSenderName(self, sender_name):
        self.sender_name = sender_name

    # 获得发送方的姓名或代号
    def GetSenderName(self):
        return self.sender_name

    # 设置接收方的姓名或代号
    def SetReceiverName(self, receiver_name):
        self.receiver_name = receiver_name

    # 获得接收方的姓名或代号
    def GetReceiverName(self):
        return self.receiver_name

    # 设置本地仓库
    def SetRepo(self, repo_dir, repo_href):
        self.repo_dir = repo_dir
        self.repo = repotools.SetRepo(repo_dir, repo_href)

    # 获得所有未加密的数据包元素列表,用来生成一个个数据包
    def GetPacketElementList(self):
        return self.packet_element_list


# 发送方的属性和基本方法
class Sender(Peer):
    # 构造函数
    def __init__(self):
        pass

    # 设置接收方公钥
    def SetReceiverPublicKey(self, receiver_public_key_file_dir):
        self.receiver_public_key = cryptotools.GetPublicKey(receiver_public_key_file_dir)

    # 获得接收方公钥
    def GetReceiverPublicKey(self):
        return self.receiver_public_key

    # 将文件转为未加密的数据
    def SetPlainText(self, file):
        with open(file, 'r', encoding='utf-8') as f:
            self.plain_data = f.read()

    # 打印出要发送的数据
    def GetPlainText(self):
        return self.plain_data

    # 将大段未加密数据分片成几片小段的未加密数据
    def SetFragmentList(self, fragment_data_length, cover_traffic_ratio):
        self.fragment_data_length = fragment_data_length
        # 生成数据流量分片列表,每个数据流量分片长度和fragment_data_length一样
        data_fragment_num = math.ceil(len(self.plain_data) / fragment_data_length)
        data_fragment_list = []
        for i in range(0, len(self.plain_data), fragment_data_length):
            data_fragment_list.append({'data': self.plain_data[i:i + fragment_data_length], 'cover_traffic': 0})
        # 生成掩护流量分片列表,每个掩护流量分片长度和fragment_data_length一样
        cover_traffic_fragment_num = int(data_fragment_num * cover_traffic_ratio)
        cover_traffic_fragment_list = []
        for i in range(0, cover_traffic_fragment_num):
            random_str = ''.join([random.choice(string.printable) for i in range(fragment_data_length)])
            cover_traffic_fragment_list.append({'data': random_str, 'cover_traffic': 1})
        # 添加上掩护流量列表,并进行随机混合
        self.plain_data_fragment_list = data_fragment_list + cover_traffic_fragment_list
        random.shuffle(self.plain_data_fragment_list)

    # 返回未加密的数据分片列表
    def GetFragmentList(self):
        return self.plain_data_fragment_list

    # 设置一系列要发送包的组成元素(头部和未加密的数据部分)的列表
    def SetPacketElementList(self):
        for i in range(0, len(self.plain_data_fragment_list)):
            packet_element = {}
            packet_element['sender_name'] = self.sender_name
            packet_element['receiver_name'] = self.receiver_name
            packet_element['cover_traffic'] = self.plain_data_fragment_list[i]['cover_traffic']
            packet_element['full_data_length'] = len(self.plain_data)
            packet_element['identification'] = 1
            packet_element['fragment_data_length'] = self.fragment_data_length
            packet_element['sn_of_fragment'] = i
            packet_element['more_fragment'] = 0 if i == len(self.plain_data_fragment_list) - 1 else 1
            packet_element['data'] = self.plain_data_fragment_list[i]['data']
            packet_element['repo_dir'] = self.repo_dir
            self.packet_element_list.append(packet_element)

    # 添加一个被加密的的文件的位置到列表里面
    def AddToEncryptedFileDirList(self, encrypted_file_dir):
        self.encrypted_file_dir_list.append(encrypted_file_dir)

    # 将所有的被加密文件传送到仓库
    def SendEncryptedFileList(self, platform):
        # 平台采用Github的话,要push的文件路径需要是相对于git仓库的路径
        if platform == "Github":
            encrypted_file_relative_dir_list = []
            for encrypted_file_dir in self.encrypted_file_dir_list:
                encrypted_file_relative_dir = encrypted_file_dir.lstrip(self.repo_dir + "/")
                encrypted_file_relative_dir_list.append(encrypted_file_relative_dir)
            repotools.PushFileList(self.repo, encrypted_file_relative_dir_list)


# 接收方的属性和基本方法
class Receiver(Peer):

    ExistentFileNameList = []   # 已经存在的所有文件名的列表
    NewAddFileNameList = []     # 新添加的文件名的列表

    # 构造函数
    def __init__(self):
        pass

    # 设置接收方私钥
    def SetReceiverPrivateKey(self, receiver_private_key_file_dir):
        self.receiver_private_key = cryptotools.GetPrivateKey(receiver_private_key_file_dir)

    # 获得接收方私钥
    def GetReceiverPrivateKey(self):
        return self.receiver_private_key

    # 从仓库接收所有被加密的文件
    def ReceiveEncryptedFileList(self, platform):
        # 记录pull操作之前,文件夹里面都有什么文件
        file_dir_dict_before = dict([(f, None) for f in glob.glob(os.path.join(self.repo_dir, '*'))])
        # 每次处理的仅仅是最新这次pull下来的文件
        if platform == "Github":
            repotools.PullAllFiles(self.repo)
            file_dir_dict_after = dict([(f, None) for f in glob.glob(os.path.join(self.repo_dir, '*'))])
            self.encrypted_file_dir_list = [f for f in file_dir_dict_after if f not in file_dir_dict_before]

    # 检查当前有没有接收完所有的包
    def CheckIntegrity(self):
        sn_list = [packet_element['sn_of_fragment'] for packet_element in self.packet_element_list]
        max_sn = max(sn_list)
        # 判断是否已经收到了max_sn之前的所有包,如果是的话检查max_sn对应的包是不是最后一个包
        if set(sn_list) == set([i for i in range(1, max_sn + 1)]):
            for packet_element in self.packet_element_list:
                if packet_element['sn_of_fragment'] == max_sn:
                    if packet_element['more_fragment'] == 0:
                        return True # 已经是最后一个包,证明接收完全
        return False
