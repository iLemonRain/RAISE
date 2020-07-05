# 和加解密相关的操作
import functiontimer
import random
import string
import rsa
import base64
from ecdsa import ECDH, NIST256p
from cryptography.hazmat.primitives.ciphers.aead import ChaCha20Poly1305
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


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
def GetRSAPublicKey(public_key_file_dir):
    with open(public_key_file_dir, 'rb') as public_key_file:
        p = public_key_file.read()
    return rsa.PublicKey.load_pkcs1(p)


# 获得私钥
def GetRSAPrivateKey(private_key_file_dir):
    with open(private_key_file_dir, 'rb') as private_file:
        p = private_file.read()
    return rsa.PrivateKey.load_pkcs1(p)


# 使用对方的公钥文件,来加密信息,并返回加密信息
def RSAEncodeData(data, public_key):
    data = data.encode('utf-8')
    return str(base64.standard_b64encode(rsa.encrypt(data, public_key)), encoding="utf-8").replace("/", "$")


# 使用自己的私钥文件,来解密信息,并返回解密信息
def RSADecodeData(data, private_key):
    return rsa.decrypt(base64.standard_b64decode(data.replace("$", "/")), private_key)


# 根据椭圆曲线类型,初始化ECDH
@functiontimer.fn_timer
def ECDHInit():
    ecdh = ECDH(NIST256p)
    ecdh.generate_private_key()
    return ecdh


# 生成ECDH所用的临时公钥(pem格式)
@functiontimer.fn_timer
def GenerateECDHPublicKey(ecdh):
    local_public_key = ecdh.get_public_key().to_pem()
    return local_public_key


# 根据自己的私钥和对方传来的公钥生成本次加密传输所需的对称秘钥:
@functiontimer.fn_timer
def GenerateECDHSharedKey(ecdh, remote_public_key):
    ecdh.load_received_public_key_pem(remote_public_key)
    shared_key = ecdh.generate_sharedsecret_bytes()
    return shared_key


# 生成一个AEAD(关联数据的认证加密)加解密用到的的12字节随机数
def GenerateAEADNonce():
    # 生成12位字符串
    str_12 = ''.join(random.sample(string.ascii_letters + string.digits, 12))
    nonce = bytes(str_12, encoding="ascii")
    return nonce


# 初始化ChaCha20-Poly1305.输入为256位密钥(32字节),返回一个cip对象
def CC20P1305Init(key):
    chacha = ChaCha20Poly1305(key)
    return chacha


# 利用96位随机数(12个字节)生成密文,并返回ChaCha20-Poly1305密文
@functiontimer.fn_timer
def CC20P1305Encrypt(chacha, nonce, unencrypted_data):
    encrypted_data = chacha.encrypt(nonce, unencrypted_data, None)
    return encrypted_data


# 利用96位随机数(12个字节)解读ChaCha20-Poly1305密文,并返回解密结果
@functiontimer.fn_timer
def CC20P1305Decrypt(chacha, nonce, encrypted_data):
    unencrypted_data = chacha.decrypt(nonce, encrypted_data, None)
    return unencrypted_data


# 初始化ChaCha20-Poly1305.输入为256位密钥(32字节),返回一个cip对象
def AES256GCMInit(key):
    aesgcm = AESGCM(key)
    return aesgcm


# 利用96位随机数(12个字节)生成密文,并返回ChaCha20-Poly1305密文
@functiontimer.fn_timer
def AES256GCMEncrypt(aesgcm, nonce, unencrypted_data):
    encrypted_data = aesgcm.encrypt(nonce, unencrypted_data, None)
    return encrypted_data


# 利用96位随机数(12个字节)解读ChaCha20-Poly1305密文,并返回解密结果
@functiontimer.fn_timer
def AES256GCMDecrypt(aesgcm, nonce, encrypted_data):
    unencrypted_data = aesgcm.decrypt(nonce, encrypted_data, None)
    return unencrypted_data


# 用公钥加密、再用私钥解密
if __name__ == '__main__':
    # 模拟RSA
    GenerateRSAKeyFile(1024)
    public_key = GetRSAPublicKey('./config/publickey.pem')
    crypto = RSAEncodeData("lemon cherry 1 328 1 100 0 1", public_key)
    print(crypto)
    private_key = GetRSAPrivateKey('./config/privatekey.pem')
    message1 = RSADecodeData(crypto, private_key)
    print(message1.decode('utf-8'))

    # # 模拟ECDH
    ecdh_1 = ECDHInit()
    local_ecdh_public_key = GenerateECDHPublicKey(ecdh_1)
    ecdh_2 = ECDHInit()
    remote_ecdh_public_key = GenerateECDHPublicKey(ecdh_2)
    shared_key_1 = GenerateECDHSharedKey(ecdh_1, remote_ecdh_public_key)
    shared_key_2 = GenerateECDHSharedKey(ecdh_2, local_ecdh_public_key)
    nonce = GenerateAEADNonce()
    if shared_key_1 == shared_key_2:
        print("两边生成了相同的ECDH秘钥:", shared_key_1)

    with open('视频测试.mp4', 'rb')as f:
        ready_file = f.read()

    chacha_1 = CC20P1305Init(shared_key_1)
    encrypted_data = CC20P1305Encrypt(chacha_1, nonce, ready_file)
    with open('CC20P1305加密.mp4', 'wb')as f:
        f.write(encrypted_data)
    chacha_2 = CC20P1305Init(shared_key_2)
    unencrypted_data = CC20P1305Decrypt(chacha_2, nonce, encrypted_data)
    with open('CC20P1305还原.mp4', 'wb')as f:
        f.write(unencrypted_data)

    aesgcm_1 = AES256GCMInit(shared_key_1)
    encrypted_data = AES256GCMEncrypt(aesgcm_1, nonce, ready_file)
    with open('AES256GCM加密.mp4', 'wb')as f:
        f.write(encrypted_data)
    aesgcm_2 = AES256GCMInit(shared_key_2)
    unencrypted_data = AES256GCMDecrypt(aesgcm_2, nonce, encrypted_data)
    with open('AES256GCM还原.mp4', 'wb')as f:
        f.write(unencrypted_data)
