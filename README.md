# weimaiClient

微脉（WeiMai）平台非官方 Python 客户端，支持扫码登录、获取群列表、查询群信息及群成员增量数据。

## 功能特性

- 🔐 **扫码登录** — 终端生成二维码，使用微脉 App 扫码完成登录认证
- 📋 **获取群列表** — 通过 WebSocket 连接网易云信 IM，自动拉取所有群组信息
- 🔍 **查询群信息** — 查询指定群组的详细信息
- 👥 **查询群成员增量** — 获取指定群组的成员增量数据
- 🔒 **AES 加解密** — 自动处理微脉 API 的 AES-ECB 加密通信

## 项目结构

```
├── main.py                  # 程序入口
├── WMPClient.py             # 核心客户端，整合登录、群操作等功能
├── WMPCipher.py             # AES-ECB 加解密模块（兼容 CryptoJS WordArray）
├── WMPMqttClient.py         # MQTT over WebSocket 客户端（用于扫码登录）
├── WMPWebsocketClient.py    # 网易云信 WebSocket 客户端（用于获取群列表）
├── requirements.txt         # Python 依赖
└── .gitignore
```

## 安装

### 环境要求

- Python 3.7+

### 安装依赖

```bash
pip install -r requirements.txt
```

依赖列表：

| 包名 | 用途 |
|------|------|
| `requests` | HTTP 请求 |
| `websocket-client` | WebSocket 连接（网易云信 IM） |
| `paho-mqtt` | MQTT over WebSocket（扫码登录） |
| `pycryptodome` | AES 加解密 |
| `qrcode` | 终端二维码生成 |

## 使用方法

```bash
python main.py
```

运行后程序会：

1. **生成登录二维码** — 在终端显示 ASCII 二维码
2. **等待扫码** — 使用微脉 App 扫描二维码完成登录
3. **拉取群列表** — 登录成功后自动获取并显示所有群组
4. **交互查询** — 进入交互模式，输入群 ID 查询群成员增量信息

```
✅ MQTT 连接成功！
登录成功🔑 imToken: xxx, token: xxx, userid: xxx

群信息: 测试群 (ID: 12345678)
群信息: 工作群 (ID: 87654321)

请输入要查询的群 ID: 12345678

群增量信息:
{
  ...
}
```

按 `Ctrl+C` 退出程序。

## 技术细节

### 通信流程

```
┌─────────┐     MQTT/WSS      ┌──────────────┐
│  客户端   │ ◄──────────────► │ 阿里云 MQTT   │  ← 扫码登录
└─────────┘                   └──────────────┘
     │
     │          WebSocket       ┌──────────────┐
     ├─────────────────────────► │ 网易云信 IM   │  ← 获取群列表
     │                          └──────────────┘
     │
     │        HTTPS + AES       ┌──────────────┐
     └─────────────────────────► │ 微脉 API     │  ← 群信息查询
                                └──────────────┘
```

### 加密方式

API 请求和响应均使用 **AES-128-ECB** 模式加密，密钥由 CryptoJS WordArray 格式的整数数组转换而来，数据经 PKCS7 填充后 Base64 编码传输。

## 许可证

本项目仅供学习和研究使用。
