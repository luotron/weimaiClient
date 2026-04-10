from WMPClient import WMPClient
import json

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