from WMPCipher import WMPCipher
from WMPMqttClient import WMPMqttClient
from urllib.parse import unquote
import requests
import json

class WMPClient:
    def __init__(self, token = None, userid=None):
        self.api_key = [808464434, 808857697, 808988723, 811937893]
        self.login_api_key = [811675698, 808726582, 808595509, 808792116]
        # 初始化固定的 Headers
        self.headers = {
            'accept': '*/*',
            'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded',
            'origin': 'https://weimai.edujia.com',
            'referer': 'https://weimai.edujia.com/home',
            'token': token,
            'userid': str(userid) if userid is not None else None,
            'useragent': 'WeiMai/web',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
        }

    def http_post(self, url, data = None):
        try:
            response = requests.post(url=url, headers=self.headers, data=data)
            response.raise_for_status() # 检查 HTTP 状态码
            raw_response = response.text
            resp_json = json.loads(raw_response)
            if resp_json['code'] == 200:
                return resp_json
            else:
                print(f"请求失败，服务器返回: {resp_json}")
                return None
        except Exception as e:
            print(f"HTTP 请求失败: {e}")
            return None
    
    def query_group_increment(self, group_id, size=5):
        """
        查询群增量信息
        :param group_id: 群组 ID
        :param size: 查询数量
        """
        url = 'https://weimai.edujia.com/wmim/h5/group/encrypt/member/query/increment.do'
        # 1. 构建原始数据
        data_obj = {"pageSize": size, "groupid":str(group_id), "endid":0}
        # 2. AES 加密
        cipher = WMPCipher(words=self.api_key)
        encrypted_str = cipher.encrypt(data_obj)
        # 3. 构造请求体 (application/x-www-form-urlencoded)
        payload = {'encryptData': encrypted_str}
        result = self.http_post(url=url, data=payload)
        if result is not None:
            try:
                decrypted_data = cipher.decrypt(result['data'])
                return decrypted_data
            except Exception as e:
                print(f"解密失败: {e}")
                return None
    
    def query_group_info(self, group_id):
        """
        查询群信息
        :param group_id: 群组 ID
        """
        url = 'https://weimai.edujia.com/wmim/h5/group/encrypt/query/info.do'
        # 1. 构建原始数据
        data_obj = {"groupid": str(group_id)}
        
        # 2. AES 加密
        cipher = WMPCipher(words=self.api_key)
        encrypted_str = cipher.encrypt(data_obj)
        
        # 3. 构造请求体 (application/x-www-form-urlencoded)
        payload = {'encryptData': encrypted_str}
        
        result = self.http_post(url=url, data=payload)
        if result is not None:
            try:
                decrypted_data = cipher.decrypt(result['data'])
                return decrypted_data
            except Exception as e:
                print(f"解密失败: {e}")
                return None
    
    def query_login_info(self):
        url = 'https://weimai.edujia.com/wmim/h5/mqtt/encrypt/consumer/query/info.do'

        result = self.http_post(url=url)
        if result is not None:
            try:
                cipher = WMPCipher(words=self.login_api_key)
                decrypted_data = cipher.decrypt(result['data'])
                return decrypted_data
            except Exception as e:
                print(f"解密失败: {e}")
                return None
    
    def login(self):
        result = self.query_login_info()
        if result is None:
            return None
        config = {
            "host": result['object']['host'],
            "client_id": result['object']['clientId'],
            "accessKey": result['object']['accessKey'],
            "password": unquote(result['object']['password']),  # URL 解码密码
        }
        login_info = {
            "app": "weimai",
            "operation": "webLogin",
            "code": result['object']['clientId']
        }
        print(login_info)
        wmp_mqtt = WMPMqttClient(**config)
        wmp_mqtt.connect()

if __name__ == "__main__":
    TOKEN = '493B0F9A-BD78-4940-B413-B18CD99CAF22'
    USERID = '9212333513008070'
    client = WMPClient()
    result = client.login()