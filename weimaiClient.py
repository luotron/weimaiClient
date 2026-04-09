from wmp_crypto import WMPCipher
import requests
import json

class WeiMaiClient:
    def __init__(self, token, userid):
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
            'userid': str(userid),
            'useragent': 'WeiMai/web',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36'
        }
    
    def query_group_info(self, group_id):
        """
        查询群信息
        :param group_id: 群组 ID
        """
        # 1. 构建原始数据
        data_obj = {"groupid": str(group_id)}
        
        # 2. AES 加密
        cipher = WMPCipher(words=self.api_key)
        encrypted_str = cipher.encrypt(data_obj)
        
        # 3. 构造请求体 (application/x-www-form-urlencoded)
        payload = {'encryptData': encrypted_str}
        
        try:
            # 4. 发送请求
            response = requests.post(url='https://weimai.edujia.com/wmim/h5/group/encrypt/query/info.do', headers=self.headers, data=payload)
            response.raise_for_status() # 检查 HTTP 状态码
            
            # 5. 解密响应内容
            # 假设返回的是原始加密字符串，如果是 JSON 结构需先提取对应字段
            raw_response = response.text
            try:
                # 尝试解析为 JSON，提取加密字段
                resp_json = json.loads(raw_response)
                if resp_json['code'] == 200:
                    data = cipher.decrypt(resp_json['data'])
                    result = data
                else:
                    print(f"请求失败，服务器返回: {resp_json}")
                    return None
            except json.JSONDecodeError:
                # 不是 JSON 格式，直接使用文本内容
                result = raw_response
            
            return result
            
        except Exception as e:
            print(f"请求或解密失败: {e}")
            return None


if __name__ == "__main__":
    TOKEN = '493B0F9A-BD78-4940-B413-B18CD99CAF22'
    USERID = '9212333513008070'
    client = WeiMaiClient(token=TOKEN, userid=USERID)
    result = client.query_group_info(group_id=54876902196)
    if result is not None:
        print("查询结果:", result)