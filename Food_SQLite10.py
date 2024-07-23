import sqlite3
import os
import shutil
from datetime import datetime

"""
# 系统默认订餐设置
def Ordering_settings():
    # 以下为系统默认订餐设置
    ordering_set = (
        1,  # 是否自动订餐
        1,  # 是否订餐早餐
        1,  # 是否订餐中餐
        1,  # 是否订餐晚餐
        0,  # 中餐是否加餐
        0,  # 晚餐是否加餐
        1,  # 是否订周六晚餐
        0,  # 周末是否订餐
        0,  # 是否吃辣
        0,  # 10 备用
        0,  # 11 备用
    )
"""


def connect_db():
    """ 连接到数据库，如果文件不存在则会创建 """
    return sqlite3.connect('food_data.db')


def create_db():
    """ 创建数据表 """
    conn = connect_db()
    cursor = conn.cursor()
    # 确保只创建一次表
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            qq_number TEXT,
            meal_account TEXT,
            password TEXT,
            cookie TEXT,
            cookie_time TEXT,
            param_1 INTEGER,
            param_2 INTEGER,
            param_3 INTEGER,
            param_4 INTEGER,
            param_5 INTEGER,
            param_6 INTEGER,
            param_7 INTEGER,
            param_8 INTEGER,
            param_9 INTEGER,
            param_10 INTEGER,
            param_11 INTEGER
        )
    ''')
    conn.commit()
    conn.close()


# 添加用户数据
def add_user(qq_number, meal_account, password, cookie, cookie_time, params):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (qq_number, meal_account, password, cookie, cookie_time, param_1, param_2, param_3, param_4, param_5, param_6, param_7, param_8, param_9, param_10, param_11)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (qq_number, meal_account, password, cookie, cookie_time, *params))
    conn.commit()
    conn.close()


# 更新用户数据
def update_user(id, qq_number, meal_account, password, cookie, cookie_time, params):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE users SET
        qq_number = ?,
        meal_account = ?,
        password = ?,
        cookie = ?,
        cookie_time = ?,
        param_1 = ?, param_2 = ?, param_3 = ?, param_4 = ?, param_5 = ?, param_6 = ?, param_7 = ?, param_8 = ?, param_9 = ?, param_10 = ?, param_11 = ?
        WHERE id = ?
    ''', (qq_number, meal_account, password, cookie, cookie_time, *params, id))
    conn.commit()
    conn.close()


# 删除用户数据
def delete_user(qq_number):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE qq_number = ?', (qq_number,))
    conn.commit()
    conn.close()


# 根据 QQ 号码或订餐账号搜索用户数据
def search_user(by, value):
    conn = connect_db()
    cursor = conn.cursor()
    if by == "qq":
        cursor.execute('SELECT * FROM users WHERE qq_number = ?', (value,))
    elif by == "meal_account":
        cursor.execute('SELECT * FROM users WHERE meal_account = ?', (value,))
    result = cursor.fetchone()
    conn.close()
    return result


# 获取指定行数的用户数据
def get_user_by_row(row_number):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users')
    rows = cursor.fetchall()
    conn.close()
    if 0 < row_number <= len(rows):
        return rows[row_number - 1]
    else:
        return None


def SQLite_main(control_number, qq_id, u_id, u_password, Ordering_set):
    """ 主函数，用于初始化数据库和演示其他功能 """
    # 创建或初始化数据库和表
    create_db()

    # 获取当前日期和时间
    now = datetime.now()
    date_str = now.strftime("%Y%m%d")
    time_str = now.strftime("%H%M%S")

    # 定义需要复制的源文件路径
    source_file = "food_data.db"

    # 定义目标文件夹路径
    target_dir = os.path.join(os.getcwd(), date_str)

    # 如果目标文件夹不存在，则创建该文件夹
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # 定义目标文件路径，文件名包含日期和时间
    target_file = os.path.join(target_dir, f"food_data_{date_str}_{time_str}.db")

    # 复制文件到目标路径
    shutil.copy2(source_file, target_file)

    print(f"数据库文件已成功复制到 {target_file}，名称是food_data_{date_str}_{time_str}.db")

    # 如果执行编号为1，查询用户。则表示按照qq搜索用户。如果是离线账户，qq_id内填写订餐账号。
    if control_number == 1:
        # 搜索订餐账号
        user_data = search_user('qq', qq_id)
        if user_data:
            print("QQ搜索用户，账号信息已返回")
            return "账号信息已返回", user_data
        else:
            print("QQ搜索用户，无此用户")
            return "无此用户", None

    # 如果执行编号为5，自动订餐，根据行号搜索数据库。
    if control_number == 5:
        # 根据行号获取第x行数据，超限则返回None，占用密码传参
        first_user = get_user_by_row(u_password)
        # print(first_user)
        if first_user:
            print(f"数据库循环行号时成功：{u_password}")
            return "信息已返回", first_user
        else:
            print(f"数据库循环行号时，索引越界：{u_password}")
            return "索引越界", None

    # 如果执行编号为6，则表示新增账号信息。
    if control_number == 6:
        add_user(qq_id, u_id, u_password, "", "", Ordering_set)

        print("账号已添加。")
        return "账号已添加", None

    # 如果执行编号为7，则表示账号密码信息更新。如果执行编号为71，则表示订餐设置更新。
    if control_number == 7 or control_number == 71:
        user_data = search_user('qq', qq_id)
        # 更新用户数据
        if user_data:
            # 提取params部分，即原来的 param_1 到 param_11
            # params = user_data[6:]
            if control_number == 7:
                update_user(user_data[0], user_data[1], u_id, u_password, user_data[4], user_data[5], user_data[6:])

            elif control_number == 71:
                update_user(user_data[0], user_data[1], user_data[2], user_data[3], user_data[4], user_data[5],
                            Ordering_set)

            print("账号信息已更新。")
            return "账号信息已更新", None
        else:
            print("用户未找到")
            return "用户未找到", None

    # 如果执行编号为8，则表示cookie更新。
    if control_number == 8:
        user_data = search_user('meal_account', u_id)
        # 更新用户数据
        if user_data:  # qq_id, u_passwor内储存的是cookie和cookie时间
            # 提取params部分，即原来的 param_1 到 param_11
            # params = user_data[6:]
            update_user(user_data[0], user_data[1], user_data[2], user_data[3], qq_id, u_password, user_data[6:])
            print("cookie已更新。")
            return "cookie已更新", None
        else:
            print("用户未找到")
            return "用户未找到", None

    # 如果执行编号为10，则表示订餐账号绑定操作。
    if control_number == 10:
        # 搜索订餐账号
        user_data = search_user('meal_account', u_id)
        # 如果返回至不为None
        if user_data:
            # 比对QQ号
            if qq_id == user_data[1]:
                # 返回账号与QQ一致，允许登录。
                print("更新账号密码")
                return "更新账号密码", None
            else:
                # 返回"指定的订餐账号已被其他QQ号绑定，如有异议，请联系管理员。"
                print("指定的订餐账号已被其他QQ号绑定，如有异议，请联系管理员。")
                return "指定的订餐账号已被其他QQ号绑定，如有异议，请联系管理员。", None
        else:
            # 如果没有搜索到账号，则搜索QQ
            # 搜索订餐账号
            user_data = search_user('qq', qq_id)
            # 如果返回至不为None
            if user_data:
                # 比对订餐账号
                if qq_id != user_data[2]:
                    # 返回本QQ号已绑定订餐账号xxxx，如需要更改绑定请回复[订餐账号解绑]。如有异议，请联系管理员。
                    # 不会有等于的情况，如果有，则在上方判断就已经通过。
                    print(
                        f"本QQ号已绑定订餐账号{user_data[2]}，如需要更改绑定请回复[订餐账号解绑]。如有异议，请联系管理员。")
                    return f"本QQ号已绑定订餐账号{user_data[2]}，如需要更改绑定请回复[订餐账号解绑]。如有异议，请联系管理员。", None

            else:
                # 新账号，允许登录。
                print("添加账号")
                return "添加账号", None

    # 如果执行编号为11，则表示离线订餐账号添加操作。QQ号处填写订餐账号
    if control_number == 11:
        # 搜索订餐账号
        user_data = search_user('meal_account', u_id)
        # 如果返回至不为None
        if user_data:
            # 比对QQ号
            if qq_id == user_data[1]:
                # 返回账号与QQ一致，允许登录。
                print("更新账号密码")
                return "更新账号密码", None
            else:
                # 返回"指定的订餐账号已被其他QQ号绑定，如有异议，请联系管理员。"
                print("指定的订餐账号已被其他QQ号绑定，如有异议，请联系管理员。")
                return "指定的订餐账号已被其他QQ号绑定，如有异议，请联系管理员。", None
        else:
            # 如果没有搜索到账号，则搜索QQ
            # 搜索订餐账号
            user_data = search_user('qq', qq_id)
            # 如果返回至不为None
            if user_data:
                # 比对订餐账号
                if qq_id != user_data[2]:
                    # 返回本QQ号已绑定订餐账号xxxx，如需要更改绑定请回复[订餐账号解绑]。如有异议，请联系管理员。
                    # 不会有等于的情况，如果有，则在上方判断就已经通过。
                    print(
                        f"本QQ号已绑定订餐账号{user_data[2]}，如需要更改绑定请回复[订餐账号解绑]。如有异议，请联系管理员。")
                    return f"本QQ号已绑定订餐账号{user_data[2]}，如需要更改绑定请回复[订餐账号解绑]。如有异议，请联系管理员。", None

            else:
                # 新账号，允许登录。
                print("添加账号")
                return "添加账号", None


if __name__ == '__main__':
    control_number = 1
    qq_id = "xxxxx"
    u_id = "88888"
    u_password = "xxxxxx"
    ordering_set = (
        1,  # 是否自动订餐
        1,  # 是否订餐早餐
        1,  # 是否订餐中餐
        1,  # 是否订餐晚餐
        0,  # 中餐是否加餐
        0,  # 晚餐是否加餐
        1,  # 是否订周六晚餐
        0,  # 周末是否订餐
        0,  # 是否吃辣
        0,  # 10 备用
        0,  # 11 备用
    )

    # 创建或初始化数据库和表
    create_db()
    # 调用主程序
    # SQLite_main(control_number, qq_id, u_id, u_password)

    # 示例：添加用户
    add_user('123456789', 'meal123', 'password123', 'cookie_data', '2020-01-01 12:00:00', ordering_set)

    # 示例：搜索用户
    user_data = search_user('qq', '123456789')
    print(user_data)

    # 示例：搜索用户
    # user_data = search_user('qq', '323424')
    # print(user_data)

    # 示例：获取第1行数据 返回None
    # first_user = get_user_by_row(1)
    # print(first_user)

    # 示例：删除用户
    # delete_user('123456789')
