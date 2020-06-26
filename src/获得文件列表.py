import os

PATH = "./repo"
# a = [b for b in os.listdir(PATH) if b[0] != "."]
# print(a)

# def get_file_list(file_path):
#     dir_list = [b for b in os.listdir(file_path) if b[0] != "."]
#     if not dir_list:
#         return
#     else:
#         # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
#         # os.path.getmtime() 函数是获取文件最后修改时间
#         # os.path.getctime() 函数是获取文件最后创建时间
#         dir_list = sorted(dir_list, key=lambda x: os.path.getctime()(os.path.join(file_path, x)))
#         # print(dir_list)
#         return dir_list
import glob
# print(glob.glob(os.path.join(PATH, '*')))

# import time
# path_to_watch = "./repo"
# before = dict([(f, None) for f in glob.glob(os.path.join(PATH, '*'))])
# while True:
#     time.sleep(10)
#     after = dict([(f, None) for f in glob.glob(os.path.join(PATH, '*'))])
#     added = [f for f in after if f not in before]
#     removed = [f for f in before if f not in after]
#     if added:
#         print(added)
#         # print("Added: ", ", ".join(added))
#     if removed:
#         print("Removed: ", ", ".join(removed))
#     before = after

# encrypted_file_dir = "/Users/iLemonRain/Documents/python projects/RAISE/repo/3.id0"
# encrypted_file = os.path.split(encrypted_file_dir)[1] # 从文件路径当中提取出文件名
# print(encrypted_file)
# encrypted_packet_header = os.path.splitext(encrypted_file)[0]
# print(encrypted_packet_header)
before = "./repo/pkPWO"
print(before)
after = before.lstrip("./repo/")
print(after)
