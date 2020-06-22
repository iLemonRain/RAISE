import os

PATH = "./unsteged"
list_dir = os.listdir(PATH)
print(list_dir)


result = []
for maindir, subdir, file_name_list in os.walk(PATH):
    for filename in file_name_list:
        apath = os.path.join(maindir, filename)
        result.append(apath)
print(result)
