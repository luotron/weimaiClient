from WMPCipher import WMPCipher
from WMPMqttClient import WMPMqttClient
from WMPWebsocketClient import WMPWebSocketClient
from urllib.parse import unquote
import requests
import json
import qrcode

class WMPClient:
    def __init__(self, token = None, userid=None, imToken=None):
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
    
    def query_group_increment(self, group_id, endid=0, size=500):
        """
        查询群增量信息
        :param group_id: 群组 ID
        :param size: 查询数量
        """
        url = 'https://weimai.edujia.com/wmim/h5/group/encrypt/member/query/increment.do'
        # 1. 构建原始数据
        if endid == 0:
            data_obj = {"pageSize": size, "groupid":str(group_id), "endid": endid}
        else:
            data_obj = {"updateTime": "{'id':" + str(endid) + ",'updateTime':''}", "pageSize": size, "groupid":str(group_id), "endid": endid}
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
        self.generate_terminal_qr(json.dumps(login_info, separators=(',', ':')))
        wmp_mqtt = WMPMqttClient(**config)
        wmp_mqtt.set_on_message_callback(self._on_mqtt_message)
        wmp_mqtt.connect()
    
    def _on_mqtt_message(self, client, userdata, msg):
        data = json.loads(msg.payload.decode('utf-8'))
        imToken = data.get("imToken")
        token = data.get("token")
        userid = data.get("userid")
        print(f"登录成功🔑 imToken: {imToken}, token: {token}, userid: {userid}")
        self.imToken = imToken
        self.token = token
        self.userid = userid
        self.headers['token'] = token
        self.headers['userid'] = str(userid)
        client.disconnect()  # 收到消息后断开 MQTT 连接
    
    def get_group_list(self):
        self.wsClient = WMPWebSocketClient(self.imToken, self.userid)
        self.wsClient.set_on_group_message_callback(self.on_group_message)
        self.wsClient.run()
    
    def on_group_message(self, group_list):
        for group in group_list:
            group_id = group['groupid']
            print(f"\n群信息: {group['groupname']} (ID: {group_id}), 成员数: {group['count']}")
        self.wsClient.disconnect()  # 获取到群列表后断开 WebSocket 连接
        
    def generate_terminal_qr(self, text):
        # 1. 配置二维码参数
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        
        # 2. 添加数据
        qr.add_data(text)
        qr.make(fit=True)

        # 3. 在终端输出二维码
        # invert=True 通常在深色背景的终端下显示更正常
        qr.print_ascii(invert=True)

if __name__ == "__main__":
    client = WMPClient()
    client.login()
    client.get_group_list()
    while True:
        try:
            group_id = input("请输入要查询的群 ID: ")
            group_id = int(group_id)
            group_info = client.query_group_increment(group_id)
            if group_info:
                print(f"\n群增量信息:\n{json.dumps(group_info, indent=2, ensure_ascii=False)}")
        except ValueError:
            print("无效的群 ID，请输入数字。")
            exit(1)
        except KeyboardInterrupt:
            print("\n程序已退出。")
            exit(0)
        except Exception as e:
            print(f"发生错误: {e}")
            exit(1)
        