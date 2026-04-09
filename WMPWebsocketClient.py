import websocket
import ssl
import json

class WMPWebSocketClient:
    def __init__(self, url, token, userid):
        self.url = url
        # 这里的 headers 严格参考你提供的截图
        self.headers = {
            "Accept-Encoding": "gzip, deflate, br, zstd",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Host": "weblink.netease.im",
            "Origin": "https://weimai.edujia.com",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
            # 注意：如果云信 SDK 需要额外的身份验证，可能需要在这里加上 token
        }
        self.ws = None

    def on_message(self, ws, message):
        print(f"--- 收到消息 ---\n{message}\n")

    def on_error(self, ws, error):
        print(f"--- 错误 ---\n{error}")

    def on_close(self, ws, close_status_code, close_msg):
        print("### 连接已关闭 ###")

    def on_open(self, ws):
        print("### 连接已建立 ###")
        # 这里通常需要发送一个初始化数据包，例如登录包
        # auth_packet = {"type": "login", "token": "..."}
        # ws.send(json.dumps(auth_packet))

    def run(self):
        # 禁用 SSL 证书验证（如果遇到自签名证书问题）
        # ssl_opt = {"cert_reqs": ssl.CERT_NONE}
        
        self.ws = websocket.WebSocketApp(
            self.url,
            header=self.headers,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # 启动长连接
        self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

# --- 使用示例 ---
if __name__ == "__main__":
    # 从你的截图中提取的 URL
    WSS_URL = "wss://weblink.netease.im/socket.io/1/websocket/f86828d1-b57e-4eab-9a49-ba07a4c336cd"
    
    # 填入你的用户信息
    TOKEN = "493B0F9A-BD78-4940-B413-B18CD99CAF22"
    USER_ID = "9212333513008070"

    client = WMPWebSocketClient(WSS_URL, TOKEN, USER_ID)
    client.run()