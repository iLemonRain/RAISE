# 本脚本定义了发送方和接收方的整体操作.
# 对单个数据分片的操作,如数据包的编码解码过程,请见files.py
import functiontimer
import os
import glob
import random
import math
import cryptotools
import repotools


# peer的属性和基本方法(操作的是整个数据流)
class Peer(object):
    # 构造函数
    def __init__(self):
        # 发送方和接收方的名字或代号
        self.sender_name = ""                # 发送方的名字或代号
        self.receiver_name = ""              # 接收方的名字或代号
        # 仓库对象
        self.repo = None                     # 仓库对象
        self.repo_dir = None                 # 仓库根目录
        # 待发送的文件名
        self.file_name = None                # 待发送的文件名
        # 自己和对方的秘钥对
        self.sender_public_key = ""          # 发送方的公钥位置
        self.sender_private_key = ""         # 发送方的私钥位置
        self.receiver_public_key = ""        # 接收方的公钥位置
        self.receiver_private_key = ""       # 接受方的私钥位置
        # 握手包的特有部分
        self.ecdh = None                     # ECDH对象
        # 和文件存储位置相关
        self.unencrypted_file_dir_list = []  # 存放所有未被加密的文件的位置列表
        self.encrypted_file_dir_list = []    # 存放所有已被加密的文件的位置列表
        # 和传输的文本数据相关
        self.fragment_data_length = -1       # 每个分片中数据的长度
        self.plain_bytes = b""               # 未加密的字节流
        self.unencrypted_fragment_list = []  # 未加密的数据分片的列表(包含数据分片和掩护流量分片)
        # ECDH出的对称秘钥
        self.shared_key = b'e\x7fx\xb2A\x04\x89Z\x06K\xf7I[fZ\xf39\xa3t\x9d\xa9Hk\xd1-6\xef\xef\xf1\xf8\xf71'

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

    # 设置本地仓库目录
    def SetRepoDir(self, repo_dir, repo_url):
        self.repo_dir = repo_dir
        self.repo = repotools.SetRepoDir(repo_dir, repo_url)

    # 获得本地仓库目录
    def GetRepoDir(self):
        return self.repo_dir

    # 获得所有未加密的数据包元素列表,用来生成一个个数据包
    def GetUnencryptedFragmentList(self):
        return self.unencrypted_fragment_list

    # 获得要发送的原始数据
    def GetPlainBytes(self):
        return self.plain_bytes

    # 获得对称秘钥
    def GetSharedKey(self):
        return self.shared_key


# 发送方的属性和基本方法
class Sender(Peer):
    # 构造函数
    def __init__(self):
        # 从基类引入基础属性
        super(Sender, self).__init__()
        self.file_name = None
        self.ecdh_local_public_key_dir = ""  # 用于ECDH的本地临时公钥位置

    # 设置接收方公钥
    def SetReceiverPublicKey(self, receiver_public_key_file_dir):
        self.receiver_public_key = cryptotools.GetRSAPublicKey(receiver_public_key_file_dir)

    # 获得接收方公钥
    def GetReceiverPublicKey(self):
        return self.receiver_public_key

    # 初始化ECDH
    def InitECDH(self):
        self.ecdh = cryptotools.ECDHInit()

    # 初始化ECDH,并生成ECDH临时公钥
    def GenerateLocalECDHPublicKey(self, ecdh_local_public_key_dir):
        cryptotools.GenerateECDHPublicKey(self.ecdh, ecdh_local_public_key_dir)
        self.ecdh_local_public_key_dir = ecdh_local_public_key_dir

    # 开始握手第一阶段,生成握手文件和掩护流量文件
    def GenerateShakeHandFragmentList(self, cover_traffic_fragment_num):
        with open(self.ecdh_local_public_key_dir, 'rb') as f:
            self.plain_bytes = f.read()
        data_fragment_list = [].append({
                                       'sender_name': self.sender_name,
                                       'receiver_name': self.receiver_name,
                                       'cover_traffic': 0,
                                       'type_of_use': 0,
                                       'file_name': None,
                                       'full_data_length': len(self.plain_bytes),
                                       'identification': None,
                                       'fragment_data_length': len(self.plain_bytes),
                                       'sn_of_fragment': None,
                                       'more_fragment': None,
                                       'timer': 1000,
                                       'nonce': None,
                                       'data': self.plain_bytes})
        cover_traffic_fragment_list = []
        for i in range(0, cover_traffic_fragment_num):
            random_bytes = os.urandom(20)  # 这就是随便定了个数
            cover_traffic_fragment_list.append({'sender_name': self.sender_name,
                                                'receiver_name': self.receiver_name,
                                                'cover_traffic': 1,
                                                'type_of_use': 0,
                                                'file_name': None,
                                                'full_data_length': len(random_bytes),
                                                'identification': None,
                                                'fragment_data_length': len(random_bytes),
                                                'sn_of_fragment': None,
                                                'more_fragment': None,
                                                'timer': 1000,
                                                'nonce': None,
                                                'data': random_bytes})
        # 添加上掩护流量列表,并进行随机混合
        self.unencrypted_fragment_list = data_fragment_list + cover_traffic_fragment_list
        random.shuffle(self.unencrypted_fragment_list)

    # 将大段未加密数据分片成几片小段的未加密数据
    # @functiontimer.fn_timer
    def GenerateDataFragmentList(self, file, fragment_data_length, cover_traffic_ratio):
        with open(file, 'rb') as f:
            self.plain_bytes = f.read()
            self.file_name = os.path.basename(f.name)
        # 生成数据流量分片列表,每个数据流量分片长度和fragment_data_length一样
        real_fragment_num = math.ceil(len(self.plain_bytes) / fragment_data_length)
        data_fragment_list = []
        for i in range(0, len(self.plain_bytes), fragment_data_length):
            sn_of_fragment = int(i / fragment_data_length)
            data_fragment_list.append({
                'sender_name': self.sender_name,
                'receiver_name': self.receiver_name,
                'cover_traffic': 0,
                'type_of_use': 1,
                'file_name': self.file_name,
                'full_data_length': len(self.plain_bytes),
                'identification': None,
                'fragment_data_length': len(self.plain_bytes[i:i + fragment_data_length]),
                'sn_of_fragment': sn_of_fragment,
                'more_fragment': 0 if sn_of_fragment == real_fragment_num - 1 else 1,
                'timer': 1000,
                'nonce': str(cryptotools.GenerateAEADNonce(), encoding="ascii"),
                'data': self.plain_bytes[i:i + fragment_data_length]})
        # 生成掩护流量分片列表,每个掩护流量分片长度和fragment_data_length一样
        cover_traffic_fragment_num = int(real_fragment_num * cover_traffic_ratio)
        cover_traffic_fragment_list = []
        for i in range(0, cover_traffic_fragment_num):
            random_bytes = os.urandom(fragment_data_length)
            cover_traffic_fragment_list.append({
                'sender_name': self.sender_name,
                'receiver_name': self.receiver_name,
                'cover_traffic': 1,
                'type_of_use': 1,
                'file_name': self.file_name,
                'full_data_length': len(self.plain_bytes),
                'identification': None,
                'fragment_data_length': len(random_bytes),
                'sn_of_fragment': -1,
                'more_fragment': -1,
                'timer': 1000,
                'nonce': str(cryptotools.GenerateAEADNonce(), encoding="ascii"),
                'data': random_bytes})
        # 添加上掩护流量列表,并进行随机混合
        self.unencrypted_fragment_list = data_fragment_list + cover_traffic_fragment_list
        random.shuffle(self.unencrypted_fragment_list)
        self.unencrypted_fragment_list = self.unencrypted_fragment_list

    # 返回未加密的数据分片列表
    def GetFragmentList(self):
        return self.unencrypted_fragment_list

    # 添加一个被加密的的文件的位置到列表里面
    def AddToEncryptedFileDirList(self, encrypted_file_dir):
        self.encrypted_file_dir_list.append(encrypted_file_dir)

    # 将所有的被加密文件传送到仓库
    # @functiontimer.fn_timer
    def SendEncryptedFileList(self, platform):
        # 平台采用Github的话,要push的文件路径需要是相对于git仓库的路径
        if platform == "Github":
            encrypted_file_name_list = []
            for encrypted_file_dir in self.encrypted_file_dir_list:
                encrypted_file_name = ''.join(os.path.splitext(os.path.split(encrypted_file_dir)[1]))  # 为了方便push,只提取文件名
                encrypted_file_name_list.append(encrypted_file_name)
            repotools.PullAllFiles(self.repo)
            repotools.PushFileList(self.repo, encrypted_file_name_list)


# 接收方的属性和基本方法
class Receiver(Peer):
    # 构造函数
    def __init__(self):
        # 从基类引入基础属性
        super(Receiver, self).__init__()
        self.file_name = None
        self.ExistentFileNameList = []   # 已经存在的所有文件名的列表
        self.NewAddFileNameList = []     # 新添加的文件名的列表

    # 设置接收方私钥
    def SetReceiverPrivateKey(self, receiver_private_key_file_dir):
        self.receiver_private_key = cryptotools.GetRSAPrivateKey(receiver_private_key_file_dir)

    # 获得接收方私钥
    def GetReceiverPrivateKey(self):
        return self.receiver_private_key

    # 从仓库接收所有被加密的文件
    # @functiontimer.fn_timer
    def ReceiveEncryptedFileList(self, platform):
        # 记录pull操作之前,文件夹里面都有什么文件
        file_dir_dict_before = dict([(f, None) for f in glob.glob(os.path.join(self.repo_dir, '*'))])
        # 每次处理的仅仅是最新这次pull下来的文件
        if platform == "Github":
            repotools.PullAllFiles(self.repo)
            # 记录pull操作之后,文件夹里面都有什么文件,并进而计算出更改了哪些文件
            file_dir_dict_after = dict([(f, None) for f in glob.glob(os.path.join(self.repo_dir, '*'))])
            self.encrypted_file_dir_list = [f for f in file_dir_dict_after if f not in file_dir_dict_before]

        # self.encrypted_file_dir_list = [f for f in file_dir_dict_before]

    # 获得所有被加密的文件的地址列表
    def GetEncryptedFileDirList(self):
        return self.encrypted_file_dir_list

    # 将收到的元素组合包加入包列表
    def AddToUnencryptedFragmentList(self, fragment_element):
        self.unencrypted_fragment_list.append(fragment_element)

    # 检查当前有没有接收完所有的包
    def CheckIntegrity(self):
        # 校验这一系列包是不是总长度信息一致
        for i in range(len(self.unencrypted_fragment_list) - 1):
            if self.unencrypted_fragment_list[i]["full_data_length"] != self.unencrypted_fragment_list[i]["full_data_length"]:
                return False
        # 检查是不是所有片段的长度加起来等于总长度
        sn_of_fragment_sum = sum([fragment_element["fragment_data_length"]
                                  for fragment_element in self.unencrypted_fragment_list])
        if sn_of_fragment_sum != self.unencrypted_fragment_list[0]["full_data_length"]:
            return False
        # 判断是否已经收到了max_sn之前的所有包,如果是的话检查max_sn对应的包是不是最后一个包
        sn_of_fragment_list = [fragment_element["sn_of_fragment"] for fragment_element in self.unencrypted_fragment_list]
        max_sn = max(sn_of_fragment_list)
        if set(sn_of_fragment_list) == set([i for i in range(0, max_sn + 1)]):
            for fragment_element in self.unencrypted_fragment_list:
                if fragment_element['sn_of_fragment'] == max_sn and fragment_element['more_fragment'] == 0:
                    self.file_name = fragment_element['file_name']
                    return True  # 已经是最后一个包,证明接收完全
        return False

    # 将包元素列表进行排序
    # @functiontimer.fn_timer
    def SortFragmentElementList(self):
        self.unencrypted_fragment_list = sorted(self.unencrypted_fragment_list, key=lambda keys: keys['sn_of_fragment'])

    # 由各包元素生成明文
    def SaveOriginalFile(self, file_folder_dir):
        self.plain_bytes = b"".join([fragment_element["data"] for fragment_element in self.unencrypted_fragment_list])
        with open(self.file_name, 'wb+')as f:
            f.write(self.plain_bytes)


class Syncer(object):
    # 构造函数
    def __init__(self, mode, repo_dir, repo_url):
        self.mode = mode            # 设定是用哪种类型的仓库,比如是git还是其他
        self.repo_dir = repo_dir
        self.repo_url = repo_url
        self.repo = None
        self.send_list = []         # 已经准备好发送的的文件列表
        self.receive_list = []      # 接收到的文件的列表

    # 初始化仓库
    # 设置本地仓库
    def InitRepo(self):
        if self.mode == 'git':
            self.repo = repotools.SetRepoDir(self.repo_dir, self.repo_url)

    # 设定待发送列表
    def SetSendList(self, send_list):
        self.send_list = send_list

    # 获得接收列表
    def GetReceiveList(self):
        return self.receive_list

    # 获得仓库目录
    def GetRepoDir(self):
        return self.repo_dir

    # 完成一次同步
    def Sync(self):
        pass
