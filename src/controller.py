import sys
import select
import time


class Controller(object):
    # 构造函数
    def __init__(self, name):
        self.name = name
        self.peer_dict = None

    # 生成一个字典,每个字典里面有和该peer通信所用的sender和receiver对象.
    def GeneratePeerDict(self):
        # 这里应该有从配置文件读取peer列表,还没有做
        self.peer_dict = {'cherry': {'sender_obj': None, 'receiver_obj': None},
                          'banana': {'sender_obj': None, 'receiver_obj': None}}


if __name__ == '__main__':
    self_name = "lemon"
    controller = Controller(self_name)
    # controller.InitECDH()
    # controller.InitRepo()
    print("您将以名字%s和其他成员进行通信" % self_name)
    mode = input("正处于被动接收模式,按1以发起握手或发送文件:")
    while True:
        if mode == '1':
            while True:
                mode = input("按1发起握手,按2发送文件,按q返回:")
                if mode == '1':  # 发起握手
                    receiver_name = input("请输入接收者名称,按q退出:")
                    if receiver_name == 'q':
                        continue
                elif mode == '2':  # 发送文件
                    file_dir = input("请输入文件路径,按q退出:")
                    if file_dir == 'q':
                        continue
                elif mode == 'q':
                    mode = input("正处于被动接收模式,按1以发起握手或发送文件:")
                    break
                else:
                    print("您输入了错误的按键,请重新选择:")
                    continue
            continue
        else:
            mode = input("您输入了错误的按键,请重新选择:")
            continue
    else:
        pass
