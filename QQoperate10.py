# 本程序为无处不在与ChatGPT一起编写的用以自动调用QQ的程序。
# 本程序的主要功能为：根据接收到的QQ消息，进行相关的程序操作。
# 本程序的辅助功能为：建立托盘图标。
# 本程序使用的QQ消息收发项目为 https://github.com/NapNeko/NapCatQQ
import threading  # 线程管理
import uvicorn  # 异步web服务器
from fastapi import FastAPI, Request  # 快速Web框架

app = FastAPI()
import requests  # 发送 HTTP 请求
import time  # 时间处理
import datetime  # 调用时间模块
import re  # 导入正则表达式
from PIL import Image  # 用于处理图像文件
import pystray  # 创建系统托盘图标
import sys  # 用于优雅退出
import signal  # 处理信号

# 调用自动订餐程序
from FOODdingqu10 import food_main
# 调用订餐数据库
from Food_SQLite10 import SQLite_main

#

# 创建一个空的日志壳子，取代HTTP服务器的强制日志记录
import uvicorn
from uvicorn.config import Config
from uvicorn.server import Server
import logging


# 创建一个空的日志壳子，取代HTTP服务器的强制日志记录
class NoLogging:
    def __init__(self, config: Config):
        pass

    def setup(self):
        pass

    def handle(self, record):
        pass


# 创建一个托盘图标
def tray_icon_thread():
    # 创建托盘图标
    image = Image.open("自建程序LOGO_S.png")  # 图标文件
    menu = pystray.Menu(pystray.MenuItem('退出', on_exit))
    icon = pystray.Icon("自建泛用控制程序 by无处不在", image, "自建泛用控制程序", menu)
    # 运行托盘图标
    icon.run()


# 托盘图标点击退出事件
def on_exit(icon, item):
    icon.stop()  # 停止托盘图标
    uvicorn_server.should_exit = True  # 设置Uvicorn服务器退出标志
    sys.exit(0)  # 优雅退出程序
    pass


# cookie 更新程序
def cookie_update(n_cookie, n_cookie_time, u_cookie, number):
    if n_cookie != u_cookie and n_cookie != "":
        # 调用数据库函数，传参操作编号8,表示更新cookie
        SQLite_main(8, n_cookie, number, n_cookie_time, None)


# 系统默认订餐设置
def Ordering_settings():
    # 以下为系统默认订餐设置
    ordering_set = (
        1,  # 是否自动订餐
        0,  # 是否订餐早餐
        1,  # 是否订餐中餐
        1,  # 是否订餐晚餐
        0,  # 中餐是否加餐
        0,  # 晚餐是否加餐
        1,  # 是否订周六晚餐
        0,  # 周末是否订餐
        1,  # 是否吃辣
        0,  # 10 备用
        0,  # 11 备用

    )

    return ordering_set


# 主要控制程序
def xuanze(user_id, r_time, r_data):
    # 获取时间
    timestamp_1 = datetime.datetime.now().strftime("%Y.%m.%d")
    timestamp_2 = datetime.datetime.now().strftime("%H:%M:%S:%f")
    # 截取前面的12个字符，包括毫秒部分
    timestamp_3 = timestamp_2[:12]

    # 初始化元组
    output = ()
    # 管理员标识
    admin = False

    # 判断是否为管理员
    if "xxxxx" in user_id or "xxxxxx" in user_id:
        admin = True

    # 文本开头
    if admin:
        user_str = f"尊敬的管理员:"
    else:
        user_str = f"亲爱的用户:{user_id}"

    # 公用控制部分
    if "当前" in r_data and "时间" in r_data:  # 检查text_content是否包含"时间"和"当前"

        output = (
                f"{user_str}\n\n"
                "程序:测试时间返回\n\n"
                f"[{timestamp_1}" + f"-{timestamp_3}]"
        )

    elif r_data.strip().lower().startswith("免责声明".lower()):
        output = (
                     f"{user_str}\n\n"

                     f"免责声明：\n"
                     f"本项目正在进行灰度测试，\n"
                     f"本项目为个人兴趣爱好编写，\n"
                     f"主要目的为学习编程方法。\n"
                     f"本项目所使用的第三方库均为GitHub开源项目。\n"
                     f"本项目准备进行GitHub开源。\n"
                     f"本项目完全免费，仅供测试者使用，不涉及任何商业用途。\n"
                     f"本项目不构成任何形式的数据破解和破坏，一切数据行为皆属于正常用户操作范围。\n"
                     f"本项目承诺不主动获取除QQ号码、订餐号码、订餐密码之外的一切个人隐私数据。\n"
                     f"本项目为作者为爱发电，喜欢言语攻击说风凉话的不要让我听见。\n\n"
                     f"如果你不同意或不认同上述内容，请删除本QQ，不要进行测试。\n\n"
        )

    elif r_data.strip().lower().startswith("功能详细说明".lower()):
        output = (
                f"{user_str}\n\n"
                f"以下是现有的程序功能详细说明：\n"
                f"————————————\n"
                f"提示：回复中括号“[”“]”内的文字即可使用。\n"
                f"举例：回复“查询订餐”即可触发相应功能。\n"
                f"————————————\n"

                f"[查询订餐]= 查询当前QQ绑定的订餐账号三天内所有的订餐信息。\n\n"
                # f"[自动订餐]= 将在每日17时50分自动按照订取明天餐食。\n\n"
                f"[订餐明天]= 根据用户订餐设置订取明天的餐食。(20时截止明日订餐)\n\n\n"
                # f"[订餐后天]= 根据用户设置订取后天的餐食，如未设置则默认订取中餐和晚餐。\n\n"
                f"[订餐账号绑定]= 根据返回的提示输入你的账号密码，用于初始绑定、更换绑定、更改密码。\n\n"
                f"[订餐设置]= 设置用户的订取时的餐次选项，包括自动订餐设置，根据返回的信息提示操作即可。\n\n"
                # f"[订餐提示]= 输出当前的用户选择的订餐需要提示的功能。"

                f"[订餐程序说明]= 返回本程序的详细功能流程。内容较多。\n\n"

                # f"[管理员指令：添加离线用户]= 根据返回提示发送账号密码，即可按照设置信息每天自动订餐，QQ号默认设置888888"
                f"当前信息发送时间：[{timestamp_1}" + f"-{timestamp_3}]"

        )

    # 检查来信是否以"帮助"或"功能"开头
    elif r_data.strip().lower().startswith("帮助".lower()) or r_data.strip().lower().startswith("功能".lower()):

        output = (
                    f"{user_str}\n\n"
                    f"————————————\n"
                    f"新用户请先绑定账号。\n"
                    f"————————————\n"
                    f"举例：回复“订餐账号绑定”即可触发相应功能。\n"
                    f"————————————\n"
                    f"提示：回复相应命令即可使用相应功能。\n"
                    f"————————————\n"
                    f"目前包含的功能有：\n"
                    f"[管理员指令]、[订餐账号绑定]、[查询订餐]、[订餐明天]、[订餐设置]、[功能详细说明]、[订餐程序说明]"
                    f"{'、[管理员指令]' if admin else ''}"
                    f"\n————————————\n"
                    f"当前信息发送时间：[{timestamp_1}" + f"-{timestamp_3}]"

        )


    elif (r_data.strip().lower().startswith("管理员功能".lower()) or r_data.strip().lower().startswith("管理员指令".lower())) and admin:
        output = (
                f"{user_str}\n\n"
                f"————————————\n"
                f"管理员指令：添加离线账户\n"
                f"账号：1111\n"
                f"密码：123456789\n"
                f"————————————\n"
                f"管理员指令：全用户通知\n"
                f"自动订餐服务器公告：\n"
                f"******\n"
                f"————————————\n"
                f"当前信息发送时间：[{timestamp_1}" + f"-{timestamp_3}]"

        )

    elif r_data.strip().lower().startswith("管理员指令：".lower()) and admin:

        if r_data.strip().lower().startswith("管理员指令：添加离线账户".lower()):
            output = (
                    f"{user_str}\n\n"
                    f"————————————\n"
                    f"功能暂无\n"
                    f"————————————\n"

            )

        if r_data.strip().lower().startswith("管理员指令：全用户通知".lower()):

            # 去除第一行内容
            lines = r_data.strip().split('\n')
            output_content = '\n'.join(lines[1:])

            # 写入output变量
            output = f"{output_content}"

            print(f"发送的全体通知：\n{output}")

            #
            for i in range(1, 1000):
                # 调用数据库函数，传参操作编号5,借用自动订餐，按照行号遍历数据库，占用订餐账号传参。
                return_data, sql_data = SQLite_main(5, "", "", i, None)
                if return_data.strip() == "索引越界":
                    print(f"全用户通知已完成，循环{i - 1}次")
                    output = (
                            f"{user_str}\n\n"
                            f"全用户通知已完成，循环{i - 1}次"
                    )

                else:

                    if sql_data[1] != "888888":
                        # 调用回信程序
                        huixin(sql_data[1], output)

    # 订餐控制部分
    if "订餐" in r_data:

        # 订餐查询天数
        days = 3

        # 是否只有特定字符
        if r_data.strip() == "查询订餐":
            # 调用数据库函数，传参操作编号1,表示查询订餐。
            return_data, sql_data = SQLite_main(1, user_id, "", "", None)
            if return_data.strip() == "无此用户":
                output = (
                    f"{user_str}\n\n"
                    f"错误：本账号未绑定订餐账号"
                )
            else:
                # 编号2，查询订餐
                err, results, n_cookie, n_cookie_time = food_main(2, sql_data[2],
                                                                  sql_data[3], sql_data[4], sql_data[5], days)

                if err == "":
                    # 更新cookie
                    cookie_update(n_cookie, n_cookie_time, sql_data[4], sql_data[2])
                    # 使用join()方法将results中的元素合并为一个字符串，每个元素之间用换行符分隔
                    output_lines = "\n".join(results)
                    # 将合并后的字符串插入到output变量中
                    output = (
                        f"{user_str}\n\n"
                        f"实时查询到的订餐如下：\n\n"
                        f"\n{output_lines}\n"
                    )
                else:
                    output = (
                        f"{user_str}\n\n"
                        f"错误：查询订餐出错\n"
                        f"[{err}]"
                    )

        if r_data.strip() == "订餐明天":
            # 调用数据库函数，传参操作编号1,表示查询用户，按照QQ搜索用户。
            return_data, sql_data = SQLite_main(1, user_id, "", "", None)
            if return_data.strip() == "无此用户":
                output = (
                    f"{user_str}\n\n"
                    f"错误：本账号未绑定订餐账号"
                )
            else:
                # 编号3，手动订餐明天
                err, results, n_cookie, n_cookie_time = food_main(3, sql_data[2],
                                                                  sql_data[3], sql_data[4], sql_data[5], days,
                                                                  sql_data[6:])

                # 获取当前日期
                current_date = datetime.datetime.now()
                # 加一天
                next_day = current_date + datetime.timedelta(days=1)

                # 格式化日期为YYYY-MM-DD
                formatted_date = next_day.strftime('%Y-%m-%d')

                if err == "":
                    # 更新cookie
                    cookie_update(n_cookie, n_cookie_time, sql_data[4], sql_data[2])

                    output = (
                        f"{user_str}\n\n"
                        f"明日({formatted_date})订餐完成\n"
                        f"当前显示余额[{results}]元\n"
                        f"可回复[查询订餐]查看已订餐详情。"
                    )
                else:
                    output = (
                        f"{user_str}\n\n"
                        f"错误：明日({formatted_date})订餐失败\n"
                        f"[{err}]"
                    )

        if r_data.strip() == "订餐设置":
            # 调用数据库函数，传参操作编号1,表示查询订餐，按照QQ搜索用户。
            return_data, sql_data = SQLite_main(1, user_id, "", "", None)
            if return_data.strip() == "无此用户":
                output = (
                    f"{user_str}\n\n"
                    f"错误：本账号未绑定订餐账号"
                )
            elif return_data.strip() == "账号信息已返回":

                # sql_data[1]
                output = (
                    f"{user_str}\n\n"
                    f"—————————————\n"
                    f"订餐设置说明\n"
                    f"—————————————\n"
                    f"如果设置有冲突，则按照常理优先。\n"
                    f"例如不定晚餐但晚餐加餐时，晚餐加餐不生效。\n"
                    f"—————————————\n"
                    f"自动订餐功能表现为每天17.35分按照订餐设置自动订餐。\n"
                    f"—————————————\n"
                    f"手动发送[订餐明天]订餐时，不受最后的日期设置管控。\n"
                    f"—————————————\n"
                    f"加餐有多个菜时，系统自动选择第一个菜。\n"
                    f"—————————————\n"
                    f"查询到绑定账号{sql_data[2]}的当前订餐设置如下：\n\n"
                    f"如果需要修改设置请复制以下消息格式，修改相应内容后发送给我。\n\n"
                    f"—————————————\n"
                    f"请复制横线以下消息回复\n"
                    f"—————————————\n"

                    f"订餐设置变更：\n"
                    f"是否启用自动订餐：{'是' if sql_data[6] == 1 else '否'}\n"
                    f"是否订餐早餐：{'是' if sql_data[7] == 1 else '否'}\n"
                    f"是否订餐中餐：{'是' if sql_data[8] == 1 else '否'}\n"
                    f"是否订餐晚餐：{'是' if sql_data[9] == 1 else '否'}\n"
                    f"是否吃辣：{'是' if sql_data[14] == 1 else '否'}\n"

                    f"中餐是否加餐：{'是' if sql_data[10] == 1 else '否'}\n"
                    f"晚餐是否加餐：{'是' if sql_data[11] == 1 else '否'}\n"

                    f"周六晚餐是否订餐：{'是' if sql_data[12] == 1 else '否'}\n"
                    f"周日是否订餐：{'是' if sql_data[13] == 1 else '否'}\n"

                    # f"1.是否启用自动订餐：{'是' if sql_data[15] == 1 else '否'}\n"
                    # f"1.是否启用自动订餐：{'是' if sql_data[16] == 1 else '否'}\n"

                )

        if r_data.strip().lower().startswith("订餐设置变更".lower()):
            # 调用数据库函数，传参操作编号1,表示查询订餐，按照QQ搜索用户。
            return_data, sql_data = SQLite_main(1, user_id, "", "", None)
            if return_data.strip() == "无此用户":
                output = (
                    f"{user_str}\n\n"
                    f"错误：本账号未绑定订餐账号"
                )
            elif return_data.strip() == "账号信息已返回":

                # 定义前缀到索引的映射
                prefix_to_index = {
                    "是否启用自动订餐：": 0,
                    "是否订餐早餐：": 1,
                    "是否订餐中餐：": 2,
                    "是否订餐晚餐：": 3,
                    "中餐是否加餐：": 4,
                    "晚餐是否加餐：": 5,
                    "周六晚餐是否订餐：": 6,
                    "周日是否订餐：": 7,
                    "是否吃辣：": 8,

                }

                # 初始化rules_data
                rules_data = [0] * len(prefix_to_index)
                # 初始化 错误标志
                rules_err1 = False
                rules_err2 = False

                # 匹配每行的前缀和内容
                pattern = re.compile(r'^(.*?：)([是|否])$', re.MULTILINE)
                matches = pattern.findall(r_data)

                # 检查是否有无效的内容
                for line in r_data.strip().split("\n"):
                    if re.match(r'^(.*?：)([是|否])$', line.strip()) is None and "订餐设置变更：" not in line:
                        # raise ValueError(f"检测到无效数据: {line.strip()}")
                        rules_err1 = True
                        break

                # 跟踪已匹配的前缀
                matched_prefixes = set()

                # 根据前缀映射存储数据
                for prefix, value in matches:
                    if prefix in prefix_to_index:
                        matched_prefixes.add(prefix)

                # 检查是否有未匹配的前缀
                for prefix in prefix_to_index:
                    if prefix not in matched_prefixes:
                        # raise ValueError(f"未检测到前缀: {prefix}")
                        rules_err2 = True
                        break

                if not rules_err1 and not rules_err2:
                    # 所有检查通过后写入元组
                    for prefix, value in matches:
                        if prefix in prefix_to_index:
                            index = prefix_to_index[prefix]
                            rules_data[index] = 1 if value == '是' else 0

                    # 转换为元组
                    # rules_data = tuple(rules_data)
                    # 使用列表推导和切片来创建一个长度固定的11位元组
                    fixed_tuple = tuple(rules_data[i] if i < len(rules_data) else 0 for i in range(11))

                    # 调用数据库函数，执行编号为71，则表示订餐设置更新。
                    return_data, _ = SQLite_main(71, sql_data[1], sql_data[2], sql_data[3], fixed_tuple)
                    if return_data.strip() == "账号信息已更新":
                        output = (
                            f"{user_str}\n\n"
                            f"订餐账号{sql_data[2]}订餐设置变更成功。"
                        )
                    else:
                        output = (
                            f"{user_str}\n\n"
                            f"错误：{return_data}\n\n"
                            f"订餐设置变更失败。"
                        )

                else:
                    if rules_err1:
                        output = (
                            f"{user_str}\n\n"
                            f"错误：检测到无效数据: {line.strip()}"
                            f"订餐设置变更失败。"
                        )
                    elif rules_err2:
                        output = (
                            f"{user_str}\n\n"
                            f"错误：未检测到设置: {prefix}"
                            f"订餐设置变更失败。"
                        )

        if r_data.strip() == "订餐账号绑定" or r_data.strip() == "订餐帐号绑定":
            output = (
                f"{user_str}\n\n"
                f"请输入你登录订餐系统的账号密码：\n\n"
                f"————————————\n"
                f"请先回复[免责声明]查阅免责声明。\n"
                f"————————————\n"
                f"提示：密码仅支持数字与大小写字母\n"
                f"————————————\n"
                f"请复制修改下面横线以下消息回复\n"
                f"————————————\n"
                f"订餐账号信息绑定或变更：\n"
                f"本人同意并认同免责声明内容。\n"
                f"订餐账号：1111\n"
                f"订餐密码：123456789"
            )

        # 是否以特定字符开头。移除首位空白并不区分大小写。
        if r_data.strip().lower().startswith("订餐账号信息绑定或变更".lower()) and "本人同意并认同免责声明内容" in r_data:

            # 调用账号密码合法性检查函数
            account_password_err, number, password = validate_account_password(r_data)
            # 如果不为空
            if account_password_err:

                output = (
                    f"{user_str}\n\n"
                    f"错误：账号密码非法\n\n"
                    f"输入的账号密码不符合要求。"
                    f"订餐账号信息绑定或变更失败。"
                )
            else:
                # 调用数据库函数，传参操作编号10,表示订餐账号绑定操作。
                return_data, sql_data = SQLite_main(10, user_id, number, password, None)
                if return_data.strip() == "更新账号密码":
                    # 编号1，调用登录验证程序
                    err, return_data, n_cookie, n_cookie_time = food_main(1, number, password, "", "", days)
                    # 如果没有错误信息
                    if err == "":
                        # 调用数据库函数，传参操作编号7,表示更新账号信息。
                        return_data, _ = SQLite_main(7, user_id, number, password, None)
                        if return_data.strip() == "账号信息已更新":

                            # 更新cookie
                            cookie_update(n_cookie, n_cookie_time, "", number)

                            output = (
                                f"{user_str}\n\n"
                                f"绑定订餐账号{number}成功。\n\n"
                                f"订餐设置采用默认设置，如需查询或更改请发送[订餐设置]。"

                            )
                        else:
                            output = (
                                f"{user_str}\n\n"
                                f"错误：{return_data}\n\n"
                                f"绑定订餐账号{number}失败。"
                            )

                    else:
                        output = (
                            f"{user_str}\n\n"
                            f"错误：{err}\n\n"
                            f"更新账号订餐账号{number}失败。"
                        )

                elif return_data.strip() == "添加账号":
                    # 编号1，调用登录验证程序
                    err, return_data, n_cookie, n_cookie_time = food_main(1, number, password, "", "", days)
                    # 如果没有错误信息
                    if err == "":
                        # 调用订餐参数默认设置
                        Ordering_set = Ordering_settings()

                        # 调用数据库函数，传参操作编号6,表示新增账号信息。
                        SQLite_main(6, user_id, number, password, Ordering_set)
                        # 更新cookie
                        cookie_update(n_cookie, n_cookie_time, "", number)

                        output = (
                            f"{user_str}\n\n"
                            f"绑定订餐账号{number}成功。"
                            f"订餐设置采用默认设置，如需查询或更改请发送[订餐设置]。"
                        )

                    else:
                        output = (
                            f"{user_str}\n\n"
                            f"错误：{err}\n\n"
                            f"绑定订餐账号{number}失败。"
                        )

                else:
                    output = (
                        f"{user_str}\n\n"
                        f"错误：{return_data}"
                        f"订餐账号信息绑定或变更失败。"
                    )

        if r_data.strip() == "订餐程序说明":
            output = (
                f"{user_str}\n\n"
                f"你正在查看订餐程序详细说明：\n\n"
                f"————————————————\n"
                f"免责声明：\n"
                f"本程序为个人兴趣爱好编写，\n"
                f"主要目的为学习编程方法。\n"
                f"本项目所使用的第三方库都是GitHub开源项目。\n"
                f"本项目准备进行GitHub开源。\n"
                f"本项目完全免费，仅供测试者使用，不涉及任何商业用途。\n"
                f"本项目不构成任何形式的数据破解和破坏，一切数据行为皆属于正常操作。\n"
                f"本项目承诺不主动获取除QQ号码、订餐号码、订餐密码之外的一切个人隐私数据。\n\n"
                f"如果你不同意或不认同上述内容，请删除本QQ，不要进行测试。\n\n"                
                f"开发者承诺下述内容均为本程序1.0版本真实功能。\n\n"

                f"本程序功能块描述：\n"
                f"1.本项目使用Python编写，版本号为3.9。\n"
                f"2.本项目使用GitHub开源项目NapCat进行QQ消息的获取与发送。\n"
                f"3.本项目使用GitHub开源项目DDDDOCR离线模型进行验证码识别。\n"
                f"4.本项目使用Python的Requests库进行HTTP通信。\n"
                f"5.本项目使用FastAPI进行服务器构建。\n"
                f"6.本项目使用SQLite进行轻量级数据库构建。\n\n"

                f"本程序查询订餐功能流程描述：\n"
                f"1.测试者向本QQ发送查询订餐指令，主程序异步调用订餐系统操作程序。\n"
                f"2.访问订餐系统账号登录界面，提取服务器返回的会话ID与Cookie值。提取验证码图片，提取百度流量key。访问时的UA为本机UA。\n"
                f"3.使用测试者提交的账号密码进行表单拼接，POST登录操作，如果该账号下拥有10小时内进行过登录的Cookie，则跳过验证码识别，直接用旧Cookie进行登录。\n"
                f"4.登录后访问订单查询界面，对返回的html进行数据分析，提取其中已订餐数据。\n"
                f"5.将提取到的数据返回给发信QQ。\n"
                f"6.该功能的HTTP请求信息均带有合法Cookie，真实UA，合理Referer。\n\n"
                
                f"本程序订餐功能流程描述(含自动订餐)：\n"
                f"1.测试者向本QQ发送订餐指令，或按照测试者设置自动触发订餐，主程序异步调用订餐系统操作程序。\n"
                f"2.访问订餐系统账号登录界面，提取服务器返回的会话ID与Cookie值。提取验证码图片，提取百度流量key。访问时的UA为本机UA。\n"
                f"3.使用测试者提交的账号密码进行表单拼接，POST登录操作，如果该账号下拥有12小时内进行过登录的Cookie，则跳过验证码识别，直接用旧Cookie进行登录。\n"
                f"4.登录后访问订单界面，对返回的html进行数据分析，提取其中的可订餐数据。\n"
                f"5.根据测试者的订餐设置，进行相应的菜品进行模拟勾选。\n"
                f"6.勾选完成后访问购物车界面，由购物车页面数据内实际的ID与Value进行订餐POST表单的构建并发送请求。\n"
                f"7.将订餐成功信息返回给发信QQ。\n"
                f"8.该功能的HTTP请求信息均带有合法Cookie，真实UA，合理Referer。"

            )


    # 如果输出元组是空的
    if not output:
        output = (
                "错误:指令非法\n\n"
                "本次输入的指令不是任何已知的指令。\n\n"
                "请回复“功能”或“帮助”查看当前支持的功能。\n\n"
                f"当前信息发送时间：[{timestamp_1}" + f"-{timestamp_3}]"
        )
    # 调用回信程序
    huixin(user_id, output)


# 账号密码合法性验证程序
def validate_account_password(text):
    # 使用正则表达式提取账号和密码
    # 确保可以处理全角或半角冒号，忽略“账号”和“密码”后面直到冒号的所有内容
    account_match = re.search(r"账号[^：:]*[：:](\d+)", text)
    password_match = re.search(r"密码[^：:]*[：:](\S+)", text)

    formatted_account_number = ""
    password = ""

    if account_match and password_match:
        # 提取正则匹配的第一组字符
        account_number = account_match.group(1)
        password = password_match.group(1)

        # 验证和格式化账号
        if len(account_number) <= 6 and account_number.isdigit():
            formatted_account_number = account_number.zfill(6)
        else:
            # print("订餐账号长度超过6位或不是纯数字")
            formatted_account_number = ""

        # 密码验证规则
        if re.match(r"^[A-Za-z0-9]+$", password):
            # print("密码验证通过，只包含数字、英文")
            pass
        else:
            # print("密码包含非法字符")
            password = ""

        # print("原始订餐账号：", formatted_account_number)
        # print("提取的订餐密码：", password)

    else:
        print("未找到订餐账号或密码")
        pass

    if formatted_account_number and password:
        # print("订餐账号：", formatted_account_number)
        # print("订餐密码：", password)
        return "", formatted_account_number, password
    else:
        print("订餐账号：", formatted_account_number)
        print("订餐密码：", password)
        return "账号或密码不合法", formatted_account_number, password


# 循环线程，用于激活自动订餐
def timed_task():
    while True:
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")

        if current_time == "17:35":
            perform_daily_task()  # 执行需要的功能
            time.sleep(60)  # 等待60秒来避免在一分钟内重复执行

        time.sleep(10)  # 每10秒检查一次时间


# 自动订餐程序，由循环线程调用
def perform_daily_task():
    # print("执行特定功能：每天17:40自动运行")
    for i in range(1, 1000):
        # 调用数据库函数，传参操作编号5,表示自动订餐，按照行号遍历数据库，占用订餐账号传参。
        return_data, sql_data = SQLite_main(5, "", "", i, None)
        if return_data.strip() == "索引越界":
            print(f"自动订餐已完成，循环{i-1}次")
            return
        else:
            # 编号4，自动订餐明天
            err, results, n_cookie, n_cookie_time = food_main(4, sql_data[2],
                                                              sql_data[3], sql_data[4], sql_data[5], 3,
                                                              sql_data[6:])

            # 获取当前日期
            current_date = datetime.datetime.now()
            # 加一天
            next_day = current_date + datetime.timedelta(days=1)

            # 格式化日期为YYYY-MM-DD
            formatted_date = next_day.strftime('%Y-%m-%d')

            if err == "":
                # 更新cookie
                cookie_update(n_cookie, n_cookie_time, sql_data[4], sql_data[2])

                output = (
                    f"亲爱的用户{sql_data[1]}：\n"
                    f"自动订餐提醒：\n\n"
                    
                    f"明日({formatted_date})订餐完成\n"
                    f"当前显示余额[{results}]元\n"
                    f"可回复[查询订餐]查看已订餐详情。"
                )
            else:
                output = (
                    f"亲爱的用户{sql_data[1]}：\n"
                    f"自动订餐提醒：\n\n"
                    
                    f"错误：明日({formatted_date})订餐失败\n"
                    f"[{err}]"
                )

            if sql_data[1] != "888888":
                # 调用回信程序
                huixin(sql_data[1], output)


# 将时间戳转换为标准时间格式
def convert_to_standard_time(epoch_time):
    # 将时间戳转换为标准时间格式
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(epoch_time))


# 回信
def huixin(user_id, data):
    try:
        response = requests.post('http://127.0.0.1:20010/send_private_msg', json={
            'user_id': user_id,
            'message': [{
                'type': 'text',
                'data': {
                    'text': data
                }
            }]
        }, timeout=2)  # 设置超时时间为2秒
        # 状态码是200，表示消息发送成功
        if response.status_code == 200:
            print("QQ消息推送成功")
        else:
            print(f"QQ消息推送失败，状态码：{response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"QQ消息推送时发生错误: {e}")


# 处理好友请求
def haoyou(u_flag, u_comment, user_id):

    time.sleep(3)  # 延时3秒

    try:
        response = requests.post('http://127.0.0.1:20010/set_friend_add_request', json={
            'flag': u_flag,
            # 'approve': True,
            # 'remark': u_comment,

        }, timeout=2)  # 设置超时时间为2秒
        # 状态码是200，表示消息发送成功
        if response.status_code == 200:
            print("好友通过推送成功")
        else:
            print(f"好友通过推送失败，状态码：{response.status_code}")

        time.sleep(3)  # 延时2秒

        output = (
            f"亲爱的用户:{user_id}\n"
            "欢迎测试自动订餐操作系统\n\n"
            f"————————————\n"
            f"请牢记:本项目不收取任何费用，不涉及任何商业用途。\n"
            f"请牢记:本项目为作者个人以学习编程为目的编写。\n"
            f"请牢记:本项目仅为代替人工操作订餐，不存在任何形式的数据攻击和破解。\n"
            f"请牢记:本项目为作者为爱发电，喜欢言语攻击说风凉话的不要让我听见。\n"
            f"————————————\n"
            "请回复“功能”或“帮助”查看当前支持的功能。\n"
        )

        huixin(user_id, output)

    except requests.exceptions.RequestException as e:
        print(f"好友通过推送时发生错误: {e}")


# 收信调用
@app.post("/")
async def root(request: Request):
    data = await request.json()  # 获取事件数据
    self_id = data.get("self_id")
    user_id = data.get("user_id")
    epoch_time = data.get("time")

    # 将时间戳转换为标准时间格式
    standard_time = convert_to_standard_time(epoch_time)
    # 提取消息键type
    message_type = data.get("message", [{}])[0].get("type")

    # 好友请求ID
    u_flag = data.get("flag")
    # 好友请求名称
    # u_comment = data.get("comment")

    if message_type == "text":
        # 提取键text内的值
        text_content = data.get("message", [{}])[0].get("data", {}).get("text")
        #  print(f"Message Content: {text_content}")

        if self_id != user_id:

            # 传参对象ID，收信时间，收信数据
            xuanze(str(user_id), standard_time, text_content)

    # message_type有值但不是空或none
    elif message_type:

        output = (
            "程序提示:请输入文字\n\n"
            # f"自身ID:[{self_id}]\n"
            # f"用户ID:[{user_id}]\n"
            f"接收时间:[{standard_time}]\n"
            f"消息内容:[消息类型不支持“{message_type}”]"
        )

        huixin(user_id, output)

    # message_type是空或none,并且有好友请求ID
    elif not message_type and u_flag:

        haoyou(u_flag, standard_time, user_id)

    return {}


if __name__ == "__main__":
    # 启动托盘图标线程
    tray_thread = threading.Thread(target=tray_icon_thread)
    tray_thread.start()

    # 创建并启动后台线程
    background_thread = threading.Thread(target=timed_task, daemon=True)
    background_thread.start()

    # 捕捉信号以优雅退出
    signal.signal(signal.SIGINT, lambda signum, frame: sys.exit(0))
    signal.signal(signal.SIGTERM, lambda signum, frame: sys.exit(0))

    # 启动Uvicorn服务器
    # uvicorn_server = uvicorn.Server(config=uvicorn.Config(app, host="127.0.0.1", port=8888))
    # uvicorn_server.run()

    # 启动Uvicorn服务器，使用日志壳子
    config = Config(app, host="127.0.0.1", port=8888, log_config=None)
    config.log_config = NoLogging(config)

    uvicorn_server = Server(config=config)
    uvicorn_server.run()
