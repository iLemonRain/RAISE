# 和RSA加解密相关的操作
import rsa
import base64


# 生成公钥私钥对文件
def GenerateRSAKeyFile(bit_num):
    (pubkey, private_key) = rsa.newkeys(bit_num)
    pub = pubkey.save_pkcs1()
    with open('./config/publickey.pem', 'wb+')as f:
        f.write(pub)
    pri = private_key.save_pkcs1()
    with open('./config/privatekey.pem', 'wb+')as f:
        f.write(pri)

# 获得公钥
def GetPublicKey(public_key_file_dir):
    with open(public_key_file_dir, 'rb') as public_key_file:
        p = public_key_file.read()
    return rsa.PublicKey.load_pkcs1(p)

# 获得私钥
def GetPrivateKey(private_key_file_dir):
    with open(private_key_file_dir, 'rb') as private_file:
        p = private_file.read()
    return rsa.PrivateKey.load_pkcs1(p)

# 使用对方的公钥文件,来加密信息,并返回加密信息
def RSAEncodeData(data, public_key):
    data = data.encode('utf-8')
    return str(base64.standard_b64encode(rsa.encrypt(data, public_key)), encoding="utf-8").replace("/", "$")


# 使用自己的私钥文件,来解密信息,并返回解密信息
def RSADecodeData(data, private_key_file_dir):
    return rsa.decrypt(base64.standard_b64decode(data.replace("$", "/")), private_key)


# 用公钥加密、再用私钥解密
if __name__ == '__main__':
    # crypto = RSAEncodeData("可能的安全风险：广播可能造成广播风暴问题可能出现恶意握手文件名用对那段时间费纳决沙雕番纳斯卡的妇女节阿萨德", 'publickey.pem')
    GenerateRSAKeyFile(512)
    public_key = GetPublicKey('./config/publickey.pem')
    crypto = RSAEncodeData("lemon cherry 1 328 1 100 0 1", public_key)
    print(crypto)
    private_key = GetPrivateKey('./config/privatekey.pem')
    message1 = RSADecodeData(crypto, private_key)
    print(message1.decode('utf-8'))
