# coding:utf-8
from files import ShakeHandFileEncoder, ShakeHandFileDecoder, DataFileEncoder, DataFileDecoder
from users import Sender, Receiver
import os
import time
import functiontimer
import cryptotools

@functiontimer.fn_timer
def sh1_sender():
    # 建立一个发送方对象,之后可以定期向仓库推送发给不同接收者的内容
    sender = Sender()
    # 设定发送者和接收者的代号
    sender.SetSenderName("lemon")
    sender.SetReceiverName("cherry")
    # 设定仓库信息
    sender.SetRepoDir('./repo_send', "https://gitee.com/iLemonRain/raise_data.git")
    # 设定接收方公钥
    sender.SetReceiverPublicKey("./config/cherry_public_key.pem")
    # 开始握手
    sender.InitECDH(ecdh_lemon)
    sender.GenerateLocalECDHPublicKey("./config/lemon_ECDH_public_key.pem")
    # 生成握手文件,并设定掩护流量分片的个数
    sender.GenerateShakeHandFragmentList(2)
    # 将每个分片的组成元素加入文件里面,并发送
    for unencrypted_fragment in sender.GetUnencryptedFragmentList():
        data_file_encoder = DataFileEncoder(unencrypted_fragment, sender.GetRepoDir(), sender.GetReceiverPublicKey(), sender.GetSharedKey())
        data_file_encoder.GenerateEncryptedFile()
        sender.AddToEncryptedFileDirList(data_file_encoder.GetEncryptedFileDir())
    # 发送所有被加密的文件到仓库
    sender.SendEncryptedFileList(platform="Github")
    del sender


@functiontimer.fn_timer
def sh1_receiver():
    # 建立一个接收方对象,之后可以定期从仓库拉取不同发送者的内容
    receiver = Receiver()
    # 设定发送者和接收者的代号
    receiver.SetSenderName("lemon")
    receiver.SetReceiverName("cherry")
    # 设定仓库信息
    receiver.SetRepoDir("./repo_receive", "https://gitee.com/iLemonRain/raise_data.git")
    receiver.InitECDH(ecdh_cherry)
    # 设定接收方私钥
    receiver.SetReceiverPrivateKey("./config/cherry_private_key.pem")
    # 从仓库pull最新的被加密的文件,并生成加密文件列表
    receiver.ReceiveEncryptedFileList(platform="Github")
    # 从接收到的被加密文件列表中找到本接受者对象想要的内容(发送方和接收方都要求对的上设定)
    for encrypted_file_dir in receiver.GetEncryptedFileDirList():
        data_file_decoder = DataFileDecoder(encrypted_file_dir, receiver.GetReceiverPrivateKey(), receiver.GetSharedKey())
        if data_file_decoder.GetTypeOfUse() == 0:  # 握手文件
            # 判断发送者和接收者是不是对的人,以及是不是掩护流量,如果符合条件的话才对这个文件进行处理
            if data_file_decoder.CheckNameAndCoverTraffic(receiver.GetSenderName(), receiver.GetReceiverName()) is True:
                receiver.GenerateECDHSharedKey(data_file_decoder.GetRemoteECDHPublicKey())


@functiontimer.fn_timer
def sh2_sender():
    # 建立一个发送方对象,之后可以定期向仓库推送发给不同接收者的内容
    sender = Sender()
    # 设定发送者和接收者的代号
    sender.SetSenderName("cherry")
    sender.SetReceiverName("lemon")
    # 设定仓库信息
    sender.SetRepoDir('./repo_send', "https://gitee.com/iLemonRain/raise_data.git")
    # 设定接收方公钥
    sender.SetReceiverPublicKey("./config/lemon_public_key.pem")
    # 开始握手
    sender.InitECDH(ecdh_cherry)
    sender.GenerateLocalECDHPublicKey("./config/cherry_ECDH_public_key.pem")
    # 生成握手文件,并设定掩护流量分片的个数
    sender.GenerateShakeHandFragmentList(2)
    # 将每个分片的组成元素加入文件里面,并发送
    for unencrypted_fragment in sender.GetUnencryptedFragmentList():
        data_file_encoder = DataFileEncoder(unencrypted_fragment, sender.GetRepoDir(), sender.GetReceiverPublicKey(), sender.GetSharedKey())
        data_file_encoder.GenerateEncryptedFile()
        sender.AddToEncryptedFileDirList(data_file_encoder.GetEncryptedFileDir())
    # 发送所有被加密的文件到仓库
    sender.SendEncryptedFileList(platform="Github")
    del sender


@functiontimer.fn_timer
def sh2_receiver():
    # 建立一个接收方对象,之后可以定期从仓库拉取不同发送者的内容
    receiver = Receiver()
    # 设定发送者和接收者的代号
    receiver.SetSenderName("cherry")
    receiver.SetReceiverName("lemon")
    # 设定仓库信息
    receiver.SetRepoDir("./repo_receive", "https://gitee.com/iLemonRain/raise_data.git")
    # 设定接收方私钥
    receiver.SetReceiverPrivateKey("./config/lemon_private_key.pem")
    receiver.InitECDH(ecdh_lemon)
    # 从仓库pull最新的被加密的文件,并生成加密文件列表
    receiver.ReceiveEncryptedFileList(platform="Github")
    # 从接收到的被加密文件列表中找到本接受者对象想要的内容(发送方和接收方都要求对的上设定)
    for encrypted_file_dir in receiver.GetEncryptedFileDirList():
        data_file_decoder = DataFileDecoder(encrypted_file_dir, receiver.GetReceiverPrivateKey(), receiver.GetSharedKey())
        if data_file_decoder.GetTypeOfUse() == 0:  # 握手文件
            # 判断发送者和接收者是不是对的人,以及是不是掩护流量,如果符合条件的话才对这个文件进行处理
            if data_file_decoder.CheckNameAndCoverTraffic(receiver.GetSenderName(), receiver.GetReceiverName()) is True:
                receiver.GenerateECDHSharedKey(data_file_decoder.GetRemoteECDHPublicKey())


@functiontimer.fn_timer
def sender():
    # 建立一个发送方对象,之后可以定期向仓库推送发给不同接收者的内容
    sender = Sender()
    # 设定发送者和接收者的代号
    sender.SetSenderName("lemon")
    sender.SetReceiverName("cherry")
    # 设定仓库信息
    sender.SetRepoDir('./repo_send', "https://gitee.com/iLemonRain/raise_data.git")
    # 设定接收方公钥
    sender.SetReceiverPublicKey("./config/cherry_public_key.pem")
    # 设定单个数据分片的长度,并进行分片,并设定真实分片和掩护流量分片的比例
    sender.GenerateDataFragmentList("./testfiles/原图.png", int(329 / 5), 1)
    # 将每个分片的组成元素加入文件里面,并发送
    for unencrypted_fragment in sender.GetUnencryptedFragmentList():
        data_file_encoder = DataFileEncoder(unencrypted_fragment, sender.GetRepoDir(), sender.GetReceiverPublicKey(), sender.GetSharedKey())
        data_file_encoder.GenerateEncryptedFile()
        sender.AddToEncryptedFileDirList(data_file_encoder.GetEncryptedFileDir())
    # 发送所有被加密的文件到仓库
    sender.SendEncryptedFileList(platform="Github")
    del sender


@functiontimer.fn_timer
def receiver():
    # 建立一个接收方对象,之后可以定期从仓库拉取不同发送者的内容
    receiver = Receiver()
    # 设定发送者和接收者的代号
    receiver.SetSenderName("lemon")
    receiver.SetReceiverName("cherry")
    # 设定仓库信息
    receiver.SetRepoDir("./repo_receive", "https://gitee.com/iLemonRain/raise_data.git")
    # 设定接收方私钥
    receiver.SetReceiverPrivateKey("./config/chry_private_key.pem")
    while True:
        # 从仓库pull最新的被加密的文件,并生成加密文件列表
        receiver.ReceiveEncryptedFileList(platform="Github")
        # 从接收到的被加密文件列表中找到本接受者对象想要的内容(发送方和接收方都要求对的上设定)
        for encrypted_file_dir in receiver.GetEncryptedFileDirList():
            data_file_decoder = DataFileDecoder(encrypted_file_dir, receiver.GetReceiverPrivateKey(), receiver.GetSharedKey())
            # 判断文件类型
            if data_file_decoder.GetTypeOfUse() == 1:  # 数据传输文件
                # 判断发送者和接收者是不是对的人,以及是不是掩护流量,如果符合条件的话才对这个文件进行处理
                if data_file_decoder.CheckNameAndCoverTraffic(receiver.GetSenderName(), receiver.GetReceiverName()) is True:
                    data_file_decoder.GenerateDataFragmentList()
                    receiver.AddToUnencryptedFragmentList(data_file_decoder.GetDataFragmentList())
        # 判断是不是已经把所有包都接受完全
        if receiver.CheckIntegrity() is True:
            break
        else:
            time.sleep(3)
    receiver.SortUnencryptedFragmentList()
    receiver.SaveOriginalFile("./")


if __name__ == '__main__':
    # 不管用户从什么位置用终端执行此py文件,都将根目录设置为此工程根目录
    work_dir = os.path.abspath(os.path.join(__file__, "../.."))
    os.chdir(work_dir)
    # 暂时需要指定ECDH
    ecdh_lemon = cryptotools.ECDHInit()
    ecdh_cherry = cryptotools.ECDHInit()
    sh1_sender()
    sh1_receiver()
    sh2_sender()
    sh2_receiver()
    # sender()
    # receiver()
