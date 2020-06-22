import configparser

cp = configparser.ConfigParser()
cp.read("conf.ini")

section = cp.sections()[1]
# print(cp.options("db"))
# print(cp.get("db","db_user")) 
