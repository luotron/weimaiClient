import ssl
from paho.mqtt import client as mqtt


class WMPMqttClient:
    def __init__(self, host, client_id, accessKey, password):
        self.host = host
        self.client_id = client_id
        self.accessKey = accessKey
        self.password = password

        # 使用 Paho 2.0 API，transport 设为 websockets
        self.client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=self.client_id,
            transport="websockets",
            protocol=mqtt.MQTTv311,  # MQTT v4 (3.1.1)，与抓包一致
        )

        # 1. 配置 WebSocket 选项
        # 路径 /mqtt，以及模拟浏览器请求头
        self.client.ws_set_options(
            path="/mqtt",
            headers={
                "Host": self.host,
                "Origin": "https://weimai.edujia.com",
                "User-Agent": (
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/146.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                "Cache-Control": "no-cache",
                "Pragma": "no-cache",
            },
        )

        # 2. 配置 TLS/SSL（wss:// 必须）
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = True
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        self.client.tls_set_context(ssl_context)

        # 3. 鉴权
        self.client.username_pw_set(self.accessKey, self.password)

        # 4. 回调绑定
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_message = self._on_message
        self.client.on_subscribe = self._on_subscribe
        self.client.on_log = self._on_log

    def _on_connect(self, client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            print("✅ MQTT 连接成功！")
            # 连接成功后立即订阅 wm_login 主题（QoS=0，与抓包一致）
            client.subscribe("wm_login", qos=0)
        else:
            print(f"❌ MQTT 连接失败，原因码: {reason_code}")

    def _on_disconnect(self, client, userdata, flags, reason_code, properties):
        print(f"🔌 连接断开，原因码: {reason_code}")

    def _on_subscribe(self, client, userdata, mid, reason_codes, properties):
        print(f"📋 订阅成功，mid={mid}, reason_codes={reason_codes}")

    def _on_message(self, client, userdata, msg):
        print(f"📩 收到消息 [{msg.topic}]: {msg.payload}")

    def _on_log(self, client, userdata, level, buf):
        print(f"🔍 LOG [{level}]: {buf}")

    def connect(self):
        print(f"正在连接 wss://{self.host}/mqtt ...")
        try:
            self.client.connect(
                self.host,
                port=443,
                keepalive=100,  # 与抓包一致：100秒
            )
            self.client.loop_forever()
        except KeyboardInterrupt:
            print("\n⏹ 用户中断，正在断开连接...")
            self.client.disconnect()
        except Exception as e:
            print(f"💥 致命错误: {e}")


if __name__ == "__main__":
    # 从抓包数据中提取的参数
    config = {
        "host": "post-cn-mp90bm2as08.mqtt.aliyuncs.com",
        "client_id": "GID_wm_login@@@0594182851507843",
        "accessKey": "LTAI5tCkgTzASLTGAQGF7F2V",
        "password": "NwhglzXtPP/guBsk5fHLhYdyIPA=",
    }

    print(config)

    wmp_mqtt = WMPMqttClient(**config)
    wmp_mqtt.connect()
