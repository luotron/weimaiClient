import websocket
import ssl
import json
import time
import threading
import requests


class WMPWebSocketClient:
    def __init__(self, token=None, userid=None):
        self.token = token
        self.userid = userid
        self.ser_counter = 0  # 消息序列号计数器
        self.base_url = "https://weblink.netease.im/socket.io/1/"
        self.ws_base_url = "wss://weblink.netease.im/socket.io/1/websocket/"
        # 严格参考 curl 抓包的 headers
        self.headers = {
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Cache-Control": "no-cache",
            "Origin": "https://weimai.edujia.com",
            "Pragma": "no-cache",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        }
        self.ws = None

    def _handshake(self):
        """
        socket.io v1 HTTP 握手，获取 session id。
        GET https://weblink.netease.im/socket.io/1/?t=<timestamp>
        返回格式: session_id:heartbeat_timeout:close_timeout:supported_transports
        例如: 79f9ec1c-be68-414b-b326-7ca461496b4d:20:25:websocket,flashsocket,htmlfile,xhr-polling,jsonp-polling
        """
        timestamp = int(time.time() * 1000)
        url = f"{self.base_url}?t={timestamp}"
        print(f">>> 握手请求: {url}")
        
        resp = requests.get(url, headers=self.headers, verify=False)
        resp.raise_for_status()
        
        body = resp.text
        print(f"<<< 握手响应: {body}")
        
        # 解析 session id
        parts = body.split(":")
        session_id = parts[0]
        heartbeat_timeout = int(parts[1]) if len(parts) > 1 else 25
        close_timeout = int(parts[2]) if len(parts) > 2 else 60
        
        print(f"    Session ID: {session_id}")
        print(f"    Heartbeat Timeout: {heartbeat_timeout}s")
        print(f"    Close Timeout: {close_timeout}s")
        
        return session_id, heartbeat_timeout

    def _next_ser(self):
        """获取下一个消息序列号"""
        self.ser_counter += 1
        return self.ser_counter

    def _build_property_message(self):
        """构建第一条消息：Property（设备/身份信息）"""
        msg = {
            "SID": 2,
            "CID": 3,
            "SER": self._next_ser(),
            "Q": [
                {
                    "t": "Property",
                    "v": {
                        "3": 16,
                        "4": "Windows 10 64-bit",
                        "6": "73",
                        "8": 1,
                        "9": 1,
                        "13": "4c5455fb23229e6ba7e96608b47798e5",
                        "18": "5693a3fa5f853bd1c654195fa9431583",
                        "19": self.userid or "9212333513008070",
                        "24": "Chrome 146.0.0.0",
                        "26": "25c0c61d7cc4fea39e6358e55e1b3d94",
                        "38": "",
                        "112": 0,
                        "1000": "735e8165691a9dd380ab55fb680e9741"
                    }
                }
            ]
        }
        return msg

    def _build_sync_message(self):
        """构建第二条消息：同步状态请求"""
        msg = {
            "SID": 5,
            "CID": 1,
            "SER": self._next_ser(),
            "Q": [
                {
                    "t": "Property",
                    "v": {
                        "1": 0,
                        "2": 0,
                        "3": 0,
                        "6": 0,
                        "7": 0,
                        "9": 0,
                        "11": 0,
                        "13": 0,
                        "14": 0,
                        "15": 0,
                        "16": 0,
                        "17": 0,
                        "22": 0,
                        "24": 0,
                        "25": 0
                    }
                }
            ]
        }
        return msg

    def _send_json(self, data):
        """发送 JSON 消息（socket.io v1 协议格式：4:::json_payload）"""
        payload = "4:::" + json.dumps(data, ensure_ascii=False, separators=(',', ':'))
        print(f">>> 发送消息: {payload}")
        self.ws.send(payload)

    def on_message(self, ws, message):
        print(f"<<< 收到消息: {message}")
        # socket.io v1 心跳：收到 "2::" 时回复 "2::"
        if message.startswith("2::"):
            print(">>> 回复心跳: 2::")
            ws.send("2::")

    def on_error(self, ws, error):
        print(f"--- 错误 ---\n{error}")

    def on_close(self, ws, close_status_code, close_msg):
        print(f"### 连接已关闭 ### code={close_status_code}, msg={close_msg}")

    def on_open(self, ws):
        print("### WebSocket 连接已建立 ###")
        # 连接建立后，依次发送两条初始化消息
        def send_init_messages():
            # 等待一小段时间，确保连接稳定
            time.sleep(0.5)

            # 第一条消息：设备/身份属性
            msg1 = self._build_property_message()
            self._send_json(msg1)

            # 短暂间隔
            time.sleep(0.3)

            # 第二条消息：同步状态请求
            msg2 = self._build_sync_message()
            self._send_json(msg2)

        # 在新线程中发送，避免阻塞 WebSocket 事件循环
        threading.Thread(target=send_init_messages, daemon=True).start()

    def run(self):
        """启动 WebSocket 长连接"""
        # 第一步：HTTP 握手获取 session id
        try:
            session_id, heartbeat_timeout = self._handshake()
        except Exception as e:
            print(f"握手失败: {e}")
            return

        # 第二步：构建 WebSocket URL
        ws_url = f"{self.ws_base_url}{session_id}"
        print(f">>> 连接 WebSocket: {ws_url}")

        # websocket.enableTrace(True)  # 取消注释可开启调试日志

        self.ws = websocket.WebSocketApp(
            ws_url,
            header=self.headers,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )

        # 启动长连接，禁用 SSL 证书验证
        self.ws.run_forever(
            sslopt={"cert_reqs": ssl.CERT_NONE},
            ping_interval=heartbeat_timeout - 5,  # 在超时前发送 ping
            ping_timeout=10
        )


# --- 使用示例 ---
if __name__ == "__main__":
    # 填入你的用户信息
    TOKEN = "493B0F9A-BD78-4940-B413-B18CD99CAF22"
    USER_ID = "9212333513008070"

    client = WMPWebSocketClient(TOKEN, USER_ID)
    client.run()
