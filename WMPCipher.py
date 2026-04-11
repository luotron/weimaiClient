import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class WMPCipher:
    def __init__(self, key=None):
        """
        初始化加解密类
        :param key: 密钥（bytes）
        """
        self.key = key
        self.mode = AES.MODE_ECB
        self.block_size = AES.block_size

    def encrypt(self, data):
        """
        加密方法
        :param data: 可以是字典(dict)或字符串(str)
        :return: Base64 编码的密文
        """
        if isinstance(data, (dict, list)):
            # 必须指定 separators 以确保生成的 JSON 字符串没有多余空格
            text = json.dumps(data, separators=(',', ':'))
        else:
            text = str(data)

        cipher = AES.new(self.key, self.mode)
        # PKCS7 填充
        padded_data = pad(text.encode('utf-8'), self.block_size)
        encrypted = cipher.encrypt(padded_data)
        return base64.b64encode(encrypted).decode('utf-8')

    def decrypt(self, b64_text):
        """
        解密方法
        :param b64_text: Base64 编码的密文字符串
        :return: 解密后的明文字符串或解析后的 JSON 对象
        """
        try:
            raw_data = base64.b64decode(b64_text)
            cipher = AES.new(self.key, self.mode)
            # 解密并移除填充
            decrypted_raw = unpad(cipher.decrypt(raw_data), self.block_size)
            decrypted_str = decrypted_raw.decode('utf-8')
            
            # 尝试自动转为 JSON
            try:
                return json.loads(decrypted_str)
            except json.JSONDecodeError:
                return decrypted_str
        except Exception as e:
            raise ValueError(f"解密失败，请检查密钥或密文格式: {e}")
        
if __name__ == "__main__":
    # 示例用法
    cipher = WMPCipher()
    res = '5H6XoowZc5kVDggIF7Ar6v1kIhCWAvQUL+LBVl4jzoCH1tYUoxl1MqK+/XWAdrV0Ya39NjruIy3+zWdNqlz8NZgwgtcpFVoJTlVmfdIRVM0laHjtXDhziTR/6jqjrehS+TWK/okfeVBOnX/v9MiTjw=='
    # 解密示例
    decrypted = cipher.decrypt(res)
    print(f"Decrypted: {decrypted}")