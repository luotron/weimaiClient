from WMPClient import WMPClient
import json
import os

client = WMPClient()
client.login()
client.get_group_list()
while True:
    try:
        group_id = input("请输入要查询的群 ID: ")
        group_id = int(group_id)
        group_info = client.query_group_info(group_id)
        if not group_info:
            print(f"未找到群 ID {group_id} 的信息。")
            continue
        group_member_count = group_info['object']['memberCount']
        member_list = []
        endid = 0
        while True:
            group_increment_info = client.query_group_increment(group_id=group_id, endid=endid)
            if group_increment_info:
                for member in group_increment_info['memberArray']:
                    member_list.append(member)
                if len(group_increment_info['memberArray']) < 500:
                    break
                endid = group_increment_info['memberArray'][-1]['id']
            else:
                break
        if os.path.exists(f"output/group_{group_id}_members.txt"):
            os.remove(f"output/group_{group_id}_members.txt")
        for member in member_list:
            # print(f"成员 ID: {member['id']}, 昵称: {member['nickname']}, wmid: {member['wmid']}")
            # 写入文件
            if not os.path.exists("output"):
                os.makedirs("output")
            with open(f"output/group_{group_id}_members.txt", "a", encoding="utf-8") as f:
                f.write(f"{member['id']}----{member['nickname']}----{member['wmid']}\n")
        print(f"\n群 ID {group_id} 的成员信息已保存到 output/group_{group_id}_members.txt")
    except ValueError:
        print("无效的群 ID，请输入数字。")
        exit(1)
    except KeyboardInterrupt:
        print("\n程序已退出。")
        exit(0)
    except Exception as e:
        print(f"发生错误: {e}")
        exit(1)