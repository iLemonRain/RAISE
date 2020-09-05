# coding:utf-8
from files import ShakeHandFileEncoder, ShakeHandFileDecoder, DataFileEncoder, DataFileDecoder
from users import Sender, Receiver
import os
import time
import functiontimer

@functiontimer.fn_timer
def sender():
    # 建立一个发送方对象,之后可以定期向仓库推送发给不同接收者的内容
    sender = Sender()
    # 设定发送者和接收者的代号
    sender.SetSenderName("lemon")
    sender.SetReceiverName("cherry")
    # 设定仓库信息
    sender.SetRepo('./repo_send', "https://gitee.com/iLemonRain/raise_data.git")
    # 设定接收方公钥
    sender.SetReceiverPublicKey("./config/remote_publickey.pem")
    # 开始握手
    # sender.InitECDH()
    # sender.GenerateLocalECDHPublicKey("local_public_key.pem")
    # sender.GenerateShakeHandFragment()
    # shake_hand = 
    # sender.StartShakeHand()
    # 设定单个数据分片的长度,并进行分片,并设定真实分片和掩护流量分片的比例
    sender.GenerateDataFragmentList("./testfiles/原图.png", int(329/5), 1)
    # 设定一系列要发送包的组成元素(头部和未加密的数据部分)的列表
    sender.AddToFragmentElementList()
    # 将每个分片的组成元素加入文件里面,并发送
    for fragment_element in sender.GetFragmentElementList():
        data_file_encoder = DataFileEncoder(fragment_element, sender.GetReceiverPublicKey())
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
    receiver.SetRepo("./repo_receive", "https://gitee.com/iLemonRain/raise_data.git")
    # 设定接收方私钥
    receiver.SetReceiverPrivateKey("./config/remote_privatekey.pem")
    while True:
        # 从仓库pull最新的被加密的文件,并生成加密文件列表
        receiver.ReceiveEncryptedFileList(platform="Github")
        # 从接收到的被加密文件列表中找到本接受者对象想要的内容(发送方和接收方都要求对的上设定)
        for encrypted_file_dir in receiver.GetEncryptedFileDirList():
            data_file_decoder = DataFileDecoder(encrypted_file_dir, receiver.GetReceiverPrivateKey(), receiver.GetSharedKey())
            # 判断发送者和接收者是不是对的人,以及是不是掩护流量,如果符合条件的话才对这个文件进行处理
            if data_file_decoder.CheckNameAndCoverTraffic(receiver.GetSenderName(), receiver.GetReceiverName()) is True:
                data_file_decoder.GenerateFragmentElement()
                receiver.AddToFragmentElementList(data_file_decoder.GetFragmentElement())
        # 判断是不是已经把所有包都接受完全
        if receiver.CheckIntegrity() is True:
            break
        else:
            time.sleep(3)
    receiver.SortFragmentElementList()
    receiver.SaveOriginalFile("./")
    # # 还原出文件来
    # with open('./testfiles/原图还原.png', 'wb+')as f:
    #     f.write(receiver.GetPlainBytes())


@functiontimer.fn_timer
def sh1_sender():
    # 建立一个发送方对象,之后可以定期向仓库推送发给不同接收者的内容
    sender = Sender()
    # 设定发送者和接收者的代号
    sender.SetSenderName("lemon")
    sender.SetReceiverName("cherry")
    # 设定仓库信息
    sender.SetRepo('./repo_send', "https://gitee.com/iLemonRain/raise_data.git")
    # 设定接收方公钥
    sender.SetReceiverPublicKey("./config/remote_publickey.pem")
    # 开始握手
    sender.InitECDH()
    sender.GenerateLocalECDHPublicKey("./config/local_ECDH_publickey.pem")
    # 生成握手文件,并设定掩护流量分片的个数
    sender.GenerateShakeHandFragmentList(2)
    # 设定一系列要发送包的组成元素(头部和未加密的数据部分)的列表
    sender.AddToFragmentElementList()
    # 将每个分片的组成元素加入文件里面,并发送
    for fragment_element in sender.GetFragmentElementList():
        shake_hand_file_encoder = ShakeHandFileEncoder(fragment_element, sender.GetReceiverPublicKey())
        shake_hand_file_encoder.GenerateEncryptedFile()
        sender.AddToEncryptedFileDirList(shake_hand_file_encoder.GetEncryptedFileDir())
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
    receiver.SetRepo("./repo_receive", "https://gitee.com/iLemonRain/raise_data.git")
    # 设定接收方私钥
    receiver.SetReceiverPrivateKey("./config/remote_privatekey.pem")
    while True:
        # 从仓库pull最新的被加密的文件,并生成加密文件列表
        receiver.ReceiveEncryptedFileList(platform="Github")
        # 从接收到的被加密文件列表中找到本接受者对象想要的内容(发送方和接收方都要求对的上设定)
        for encrypted_file_dir in receiver.GetEncryptedFileDirList():
            data_file_decoder = DataFileDecoder(encrypted_file_dir, receiver.GetReceiverPrivateKey(), receiver.GetSharedKey())
            # 判断发送者和接收者是不是对的人,以及是不是掩护流量,如果符合条件的话才对这个文件进行处理
            if data_file_decoder.CheckNameAndCoverTraffic(receiver.GetSenderName(), receiver.GetReceiverName()) is True:
                data_file_decoder.GenerateFragmentElement()
                receiver.AddToFragmentElementList(data_file_decoder.GetFragmentElement())
        # 判断是不是已经把所有包都接受完全
        if receiver.CheckIntegrity() is True:
            break
        else:
            time.sleep(3)
    receiver.SortFragmentElementList()
    receiver.SaveOriginalFile("./")
    # # 还原出文件来
    # with open('./testfiles/原图还原.png', 'wb+')as f:
    #     f.write(receiver.GetPlainBytes())


if __name__ == '__main__':
    # 不管用户从什么位置用终端执行此py文件,都将根目录设置为此工程根目录
    work_dir = os.path.abspath(os.path.join(__file__, "../.."))
    os.chdir(work_dir)
    sender()
    receiver()
    # sh1_sender()
