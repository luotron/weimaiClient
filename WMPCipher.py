import json
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class WMPCipher:
    def __init__(self, words=None):
        """
        初始化加解密类
        :param words: 列表格式的 CryptoJS WordArray (如 [808464434, ...])
        """
        if words is None:
            # API Key (bytes): b'0002060a08030e0e'
            words = [808464434, 808857697, 808988723, 811937893]
            # Login Key (bytes): b'0a02040602050504'
            # words = [811675698, 808726582, 808595509, 808792116]
        
        self.key = self._convert_words_to_bytes(words)
        self.mode = AES.MODE_ECB
        self.block_size = AES.block_size

    def _convert_words_to_bytes(self, words):
        """内部方法：将 WordArray 转换为字节流"""
        key_bytes = b''
        for word in words:
            # 确保按大端序转换为 4 字节
            key_bytes += (word & 0xFFFFFFFF).to_bytes(4, byteorder='big')
        return key_bytes

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