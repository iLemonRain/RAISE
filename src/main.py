# coding:utf-8
from files import FileEncoder, FileDecoder
from users import Sender, Receiver
import os
import time

if __name__ == '__main__':
    # 不管用户从什么位置用终端执行此py文件,都将根目录设置为此工程根目录
    work_dir = os.path.abspath(os.path.join(__file__, "../.."))
    os.chdir(work_dir)

    # 建立一个发送方对象,之后可以定期向仓库推送发给不同接收者的内容
    sender = Sender()
    # 设定发送者和接收者的代号
    sender.SetSenderName("lemon")
    sender.SetReceiverName("cherry")
    # 设定仓库信息
    sender.SetRepo('./repo', "https://github.com/iLemonRain/testgithubcovertcommunication.git")
    # 设定接收方公钥
    sender.SetReceiverPublicKey("./config/publickey.pem")
    # 在当前的测试中,暂不涉及传输文件,只传输一段文字
    sender.SetPlainText("./src/原文.txt")
    # 设定单个数据分片的长度为100个字符,并进行分片,掩护流量比率为1:1
    sender.SetFragmentList(100, 1)
    # 设定一系列要发送包的组成元素(头部和未加密的数据部分)的列表
    sender.GeneratePacketElementList()
    # 将每个分片的组成元素加入文件里面,并发送
    for packet_element in sender.GetPacketElementList():
        encoder = FileEncoder(packet_element, sender.GetReceiverPublicKey())
        encoder.GenerateEncryptedFile()
        sender.AddToEncryptedFileDirList(encoder.GetEncryptedFileDir())
    # 发送所有被加密的文件到仓库
    sender.SendEncryptedFileList(platform="Github")

    # # 建立一个接收方对象,之后可以定期从仓库拉取不同发送者的内容
    # receiver = Receiver()
    # # 设定发送者和接收者的代号
    # receiver.SetSenderName("lemon")
    # receiver.SetReceiverName("cherry")
    # # 设定仓库信息
    # receiver.SetRepo("./repo", "https://github.com/iLemonRain/testgithubcovertcommunication.git")
    # # 设定接收方私钥
    # receiver.SetReceiverPrivateKey("./config/privatekey.pem")
    # while True:
    #     # 从仓库pull最新的被加密的文件,并生成加密文件列表
    #     receiver.ReceiveEncryptedFileList(platform="Github")
    #     # print(receiver.GetEncryptedFileDirList())
    #     # 从接收到的被加密文件列表中找到本接受者对象想要的内容(发送方和接收方都要求对的上设定)
    #     for encrypted_file_dir in receiver.GetEncryptedFileDirList():
    #         decoder = FileDecoder(encrypted_file_dir, receiver.GetReceiverPrivateKey())
    #         # print(decoder.unencrypted_packet_header)
    #         # 判断发送者和接收者是不是对的人,以及是不是掩护流量,如果符合条件的话才对这个文件进行处理
    #         if decoder.CheckNameAndCoverTraffic(receiver.GetSenderName(), receiver.GetReceiverName()) is True:
    #             # print(decoder.unencrypted_packet_header)
    #             print("")
    #             decoder.GeneratePacketElement()
    #             print("")
    #             # print(decoder.GetPacketElement())
    #             receiver.AddToPacketElementList(decoder.GetPacketElement())
    #     # 判断是不是已经把所有包都接受完全
    #     if receiver.CheckIntegrity() is True:
    #         break
    #     else:
    #         time.sleep(3)
    # receiver.SortPacketElementList()
    # plain_text = receiver.GeneratePlainText()
    # print(plain_text)
