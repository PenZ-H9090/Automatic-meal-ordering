import datetime  # 导入datetime库，用于获取当前时间
import hashlib  # 导入hashlib库，用于进行MD5加密
import io
import os  # 导入os库，用于操作文件系统
import re  # 导入re库，用于正则表达式匹配
import time
from PIL import Image, ImageFile
import requests  # 导入requests库，用于HTTP请求
from bs4 import BeautifulSoup

import ddddocr  # DDDDOCR验证码识别项目;https://github.com/sml2h3/ddddocr

# 本上传项目已经将所有url脱敏处理，请自行填写。


# 根据现有订餐设置，判断是否需要订餐。
def orders_rules(o_set, o_number):
    """
        # 以下为系统默认订餐设置
        o_set = (
            1,  # 是否自动订餐
            0,  # 是否订餐早餐
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
    # 程序需要返回是否需要订早餐、中餐、晚餐、中餐是否需要加餐，晚餐是否需要加餐
    # 如果是自动订餐触发并且用户设置需要自动订餐，
    # 编号3为手动订餐，编号4为自动订餐
    if (o_number == 4 and o_set[0] == 1) or o_number == 3:

        # 获取当前日期
        today = datetime.datetime.today()
        # 计算明天的日期
        tomorrow = today + datetime.timedelta(days=1)
        # 获取明天是周几
        today = tomorrow.weekday()  # 0 = 周一, 6 = 周日

        # 如果为周日，则为Ture
        is_weekend = today == 6  # 5 = 周六, 6 = 周日
        # 如果为周六，则为Ture
        is_saturday = today == 5

        if is_weekend and o_set[7] == 0 and o_number == 4:
            return "周末不订餐"

        # 订早餐
        breakfast = o_set[1]
        # 订中餐
        lunch = o_set[2]
        # 如果订中餐，则是否加餐
        extra_lunch = o_set[4] if lunch == 1 else 0

        if (is_saturday and o_set[6] == 1) or not is_saturday or o_number == 3:
            # 订晚餐
            dinner = o_set[3]
            # 如果订晚餐，则是否加餐
            extra_dinner = o_set[5] if dinner == 1 else 0
        else:
            # 不定晚餐
            dinner = 0
            extra_dinner = 0

        # 订中餐
        pepper = o_set[8]

        return (breakfast, lunch, extra_lunch, dinner, extra_dinner, pepper)

    else:
        return "不自动订餐"


# cookie有效期验证
def validate_cookie(cookie, cookie_timestamp):

    if cookie:
        # 设置cookie有效期，单位小时
        expiry_hours = 8
        # 获取当前时间
        current_time = datetime.datetime.now()

        # 将cookie生成时间戳转换为datetime对象
        cookie_time = datetime.datetime.fromtimestamp(int(cookie_timestamp))

        # 计算cookie的有效期
        expiry_time = cookie_time + datetime.timedelta(hours=expiry_hours)

        # 判断当前时间是否超过cookie的有效期
        if current_time > expiry_time:
            # 如果超过了有效期，将cookie置为空
            cookie = ""

    return cookie


# 提取新增的HMACCOUNT cookie
def fetch_hmac_count(hm_js, user_agent):
    # 定义请求的URL，使用从之前的函数中获取的hm_js值
    url = f"https://hm.baidu.com/hm.js?{hm_js}"

    # 定义请求头
    headers = {
        'User-Agent': user_agent,
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Host': 'hm.baidu.com',
        'Referer': 'http://脱敏改写-请自行填写:99/',
        'Sec-Fetch-Dest': 'script',
        'Sec-Fetch-Mode': 'no-cors',
        'Sec-Fetch-Site': 'cross-site',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"'
    }

    # 发送GET请求
    response = requests.get(url, headers=headers)

    # 从响应的标头中提取HMACCOUNT的值
    if 'HMACCOUNT' in response.cookies:
        hmac_count = response.cookies['HMACCOUNT']
        print("HMACCOUNT:", hmac_count)
        return hmac_count
    else:
        print("HMACCOUNT not found in the response headers.")
        return None


# 页面初始化程序，负责获取服务器cookie键名与键值，获取验证码，获取百度日志秘钥
def fetch_initial_data(user_agent):
    # 允许加载损坏的图片
    ImageFile.LOAD_TRUNCATED_IMAGES = True

    # 定义网址和请求头
    url = "http://脱敏改写-请自行填写:99/wxdc/index.asp"
    headers = {'User-Agent': user_agent}
    # 发起HTTP GET请求，获取初始页面数据
    response = requests.get(url, headers=headers)
    # 从响应中获取并打印cookies
    cookies = response.cookies.get_dict()
    # print("Cookies:", cookies)
    # 从响应中提取百度日志秘钥
    response_text = response.text
    match = re.search(r"hm\.baidu\.com/hm\.js\?([a-z0-9]+)", response_text)
    if match:
        hm_js = match.group(1)
        # print("已获取到百度日志秘钥:", hm_js)
        # 提取新增的HMACCOUNT cookie
        hmac_count = fetch_hmac_count(hm_js, user_agent)
        if not hmac_count:
            print("获取百度hmac_count失败")
            hm_js = None
            hmac_count = None
    else:
        print("获取百度日志秘钥失败")
        hm_js = None
        hmac_count = None

    # 获取验证码图片并保存
    captcha_url = "http://脱敏改写-请自行填写:99/wxdc/Code_1.Asp?checkcodename=usercode"
    captcha_response = requests.get(captcha_url, cookies=cookies, headers=headers)

    # 使用PIL加载图片
    with Image.open(io.BytesIO(captcha_response.content)) as img:
        # 确保图片是在RGB模式
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # 计算图片中最常见的颜色
        colors = img.getcolors(img.width * img.height) or img.convert("RGB").getcolors(img.width * img.height)
        most_common_color = max(colors, key=lambda x: x[0])[1]

        # 在图片四周添加10像素的边框
        bordered_img = Image.new('RGB', (img.width + 20, img.height + 20), most_common_color)
        bordered_img.paste(img, (10, 10))

        # 将处理后的图片保存为字节
        img_byte_arr = io.BytesIO()
        bordered_img.save(img_byte_arr, format='PNG')
        img_bytes = img_byte_arr.getvalue()

        # 保存处理后的图片为PNG (可选)
        # image_folder = '验证码'
        # os.makedirs(image_folder, exist_ok=True)
        # output_path = os.path.join(image_folder, datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".png")
        # bordered_img.save(output_path, format="PNG")
        # print("已保存验证码:", output_path)

    return cookies, hm_js, hmac_count, img_bytes


# 登录程序，负责账号密码登录，或者cookie登录
def perform_login(cookies, user_agent, user_id, user_pwd, detected_text):
    session = requests.session()
    session.headers = {'User-Agent': user_agent}
    session.cookies = requests.cookies.cookiejar_from_dict(cookies)

    # user_id = input("请输入账号: ")[:6].zfill(6)
    # user_pwd = input("请输入密码: ")
    md5_pwd = hashlib.md5(user_pwd.encode()).hexdigest()
    # captcha_code = input("请输入验证码: ")
    user_id_f = user_id[:6].zfill(6)

    data = {
        "action": "login",
        "UserID": user_id_f,
        "UserPwd": md5_pwd,
        "txt_check": detected_text,
        "%CC%E1%BD%BB": "%D7%A2%B2%E1%C8%CB%D4%B1%B5%C7%C2%BC",
    }
    # print("发送的个人信息:", data)
    login_url = "http://脱敏改写-请自行填写:99/wxdc/index.asp?action=login"
    session.post(login_url, data=data)
    response = session.get(login_url)
    # print("发送的请求头:", response.request.headers)
    return response


# 订单查询，识别订单关键字。
def query_orders(cookies, user_agent, days):
    # 构建请求的URL
    order_url = "http://脱敏改写-请自行填写:99/wxdc/OrderList3.asp"
    headers = {'User-Agent': user_agent}
    session = requests.session()
    session.headers = headers
    session.referer = "http://脱敏改写-请自行填写:99/wxdc/main.asp"  # 绕过防盗链
    session.cookies = requests.cookies.cookiejar_from_dict(cookies)

    # 发起请求
    response = session.get(order_url)
    content = response.content.decode('gb2312', errors='replace')

    # 获取今天的日期
    today = datetime.datetime.today()

    # 生成需要匹配的日期列表
    date_list = [(today + datetime.timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

    # 使用正则表达式提取相关信息
    results = []
    pattern = re.compile(
        r"<tr  bgcolor=\"#FFFFFF\" >\s*"
        r"<td height=\"25\" colspan=\"6\" align=\"center\" bgcolor=\"#DCECFA\">(.*?)</td>\s*</tr>\s*"
        r"<tr  bgcolor=\"#FFFFFF\" >.*?bgcolor=\"#FFFFFF\"><span style=\"color:#FF6a19\">(.*?)</span></td>.*?"
        r"<td width=\"0\" align=\"center\" bgcolor=\"#FFFFFF\">￥\d+</td>\s*"  # 忽略第一个价格
        r"<td width=\"0\" align=\"center\" bgcolor=\"#FFFFFF\">￥\d+</td>\s*"  # 忽略第二个价格
        r"<td width=\"0\" align=\"center\" bgcolor=\"#FFFFFF\">￥(\d+)</td>.*?"  # 最终的价格
        r"<td width=\"0\" align=\"center\">\s*(.*?)<br>", re.S)

    # 假设 content 是包含 HTML 内容的字符串
    matches = pattern.findall(content)

    for match in matches:
        date_meal = match[0]  # 日期和餐次，例如"2024-07-03(星期三)&nbsp;中餐"
        meal_details_html = match[1]  # 包含菜品的HTML部分
        total_cost = match[2]  # 最终消费
        status_html = match[3]  # 状态的HTML片段 # 状态，如"未取"或"已取"

        # 检查状态HTML片段的长度，如果长度大于2，则使用正则匹配提取“已取”
        if len(status_html) > 2:
            status = re.search(r">(\S{2})<", status_html).group(1)
        else:
            status = status_html.strip()  # 否则直接使用“未取”

        # 清理餐次字符串
        date_meal_clean = date_meal.replace('&nbsp;', ' ')

        # 提取日期部分，去掉括号和星期
        date_only = re.match(r"(\d{4}-\d{2}-\d{2})", date_meal_clean).group(1)

        # 检查日期是否在需要匹配的日期列表中
        if date_only in date_list:
            # 解析菜品详情，移除'<br>'和数字数量部分
            meal_details = re.findall(r"([^<]+) \d+份(?:<br>|$)", meal_details_html)
            meals = ', '.join(meal_details).replace('<br>', '')  # 转换为逗号分隔的字符串，移除残余的'<br>'

            # 调整结果格式
            result = f"{date_meal_clean}。{status}。\n{meals}，总消费{total_cost}元。"
            results.append(result)

    # 打印最终结果
    # print(results)  # ['2024-07-03(星期三) 中餐。未取。\n地三鲜, 咕噜肉, 剁椒蒸鱼（辣），总消费3元。', '2024-07-03(星期三) 晚餐。未取。\n酸豆角炒鸡肾, 红烧肉焖黄豆（辣），总消费0元。', '2024-07-04(星期四) 中餐。未取。\n蒜心炒腊肠, 红烧狮子头（辣），总消费0元。']

    return results, response.status_code


# 账号登录整个流程，包括初始化页面、验证码识别、账号登录
def account_login(u_id, u_password, u_cookie, cookie_time):
    # 设置全局变量UA，方便统一修改
    user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 脱敏改写-请自行填写"

    # 验证码初始化
    detected_text = "9999"
    # 验证码重试次数
    retries = 4
    for attempt in range(retries):

        # 起始请求页面，获取cookie和百度日志key和img_bytes
        cookies, hm_js, hmac_count, img_bytes = fetch_initial_data(user_agent)
        # cookie有效期验证
        u_cookie = validate_cookie(u_cookie, cookie_time)

        # 如果没有存活的cookie，则执行ORC
        if not u_cookie:
            # 调用ORC接口识别验证码
            detected_text = d_ocr(img_bytes)

            if detected_text == "":
                print(f"验证码识别失败，尝试第 {attempt + 1} 次")
                # 延时1秒
                time.sleep(1)
                if attempt == retries - 1:
                    hm_js = ""
                    print(f"验证码识别失败，超出最大重试次数。")
                    return "验证码识别失败已保存验证码，超出最大重试次数。", None, None, None, None
            else:
                # 创建一个包含初始 cookie 的字典
                cookie_dict = cookies.copy()
                # 添加额外的两个cookie项
                current_timestamp = int(datetime.datetime.now().timestamp())
                cookie_dict[f"Hm_lvt_{hm_js}"] = str(current_timestamp)
                cookie_dict[f"Hm_lpvt_{hm_js}"] = str(current_timestamp)
                cookie_dict[f"HMACCOUNT"] = str(hmac_count)

                break

        else:  # 如果已经有存活的cookie，则不执行ORC并将cookie替换

            # 创建一个包含初始 cookie 的字典
            cookie_dict = cookies.copy()

            # 如果已经有存活的cookie，更新第一个键的值
            # 将字典 cookie_dict 转换为一个迭代器。迭代器是一个可以逐个访问元素的对象。
            # next 函数从迭代器中获取下一个元素。在这里，它获取的是字典 cookie_dict 中的第一个键。
            # first_key = next(iter(cookie_dict))
            # 将 cookie_dict 中第一个键对应的值更新为新的 u_cookie。
            # cookie_dict[first_key] = u_cookie

            # 查找并更新包含固定前缀键的值
            for key in cookie_dict:
                if key.startswith("ASPSESSIONID"):
                    cookie_dict[key] = u_cookie
                    break

            # 添加额外的两个cookie项
            current_timestamp = int(datetime.datetime.now().timestamp())
            cookie_dict[f"Hm_lvt_{hm_js}"] = str(current_timestamp)
            cookie_dict[f"Hm_lpvt_{hm_js}"] = str(current_timestamp)
            cookie_dict[f"HMACCOUNT"] = str(hmac_count)

            break

    # 如果hm_js不为空
    if hm_js:

        # 重试次数
        retries = 2
        for attempt in range(retries):

            # 登录订餐系统
            login_response = perform_login(cookie_dict, user_agent, u_id, u_password, detected_text)
            print("登录通信状态代码", login_response.status_code)
            # 通信状态码不为200
            if login_response.status_code != 200:
                # 延时1秒
                time.sleep(1)
                if attempt == retries - 1:
                    print("登录时服务器无响应")
                    return "登录时服务器无响应", None, None, None, None
                continue

            # 查找包含固定前缀键的值
            for key in cookie_dict:
                if key.startswith("ASPSESSIONID"):
                    n_cookie = cookie_dict[key]
                    break
            for key in cookie_dict:
                if key.startswith("Hm_lvt_"):
                    n_cookie_time = cookie_dict[key]
                    break

            # 如果新cookie不等于老cookie
            if n_cookie != u_cookie and n_cookie != "":
                u_cookie = n_cookie
                cookie_time = n_cookie_time

            # 提取编码解码内容
            decoded_content = login_response.content.decode('gb2312', errors='replace')
            # print("收到的html:", decoded_content)

            keyword = "帐号不能为空"
            # 检查关键字是否在文本中
            if keyword in decoded_content:
                return "登录失败,账号或密码或验证码不正确", None, None, None, None
            else:
                return "", cookie_dict, user_agent, u_cookie, cookie_time

    else:
        return "页面初始化程序执行失败", None, None, None, None


# 查询订餐整个流程，包含调用登录函数、订单查询
def query_orders_1(login_err, cookie_dict, user_agent, days):
    if login_err == "":

        # 重试次数
        retries = 2
        for attempt in range(retries):
            # 查询已订餐项目
            results, status_code = query_orders(cookie_dict, user_agent, days)

            # 通信状态码不为200
            if status_code != 200:
                # 延时1秒
                time.sleep(1)
                if attempt == retries - 1:
                    print("查询订餐项目时服务器无响应")
                    return "查询订餐项目时服务器无响应", None
                break

            print("查询订单通信状态代码", status_code)

            # for result in results:
            # print(result)
            return "", results
    else:
        return login_err, None


# 订餐整个流程，包含调用登录函数、获取点单页面，选餐，购物车表单生成，提取余额，购物车提交。
def Order_food(cookies, user_agent, order_tuple):
    # 重试次数
    retries = 2
    for attempt in range(retries):
        # 获取当前日期
        current_date = datetime.datetime.now()

        # 调试时增加天数
        # current_date = current_date + datetime.timedelta(days=1)

        # 加一天
        next_day = current_date + datetime.timedelta(days=1)
        # 格式化日期为YYYY-MM-DD
        formatted_date = next_day.strftime('%Y-%m-%d')
        current_date = current_date.strftime('%Y-%m-%d')

        # 构建请求的URL
        order_url = f"http://脱敏改写-请自行填写:99/wxdc/shop3.asp?shopid=0&gtype=&dt2={formatted_date}"
        headers = {'User-Agent': user_agent}
        session = requests.session()
        session.headers = headers
        session.referer = f"http://脱敏改写-请自行填写:99/wxdc/shop3.asp?shopid=0&gtype=&dt2={current_date}"  # 绕过防盗链
        session.cookies = requests.cookies.cookiejar_from_dict(cookies)

        # 发起请求
        response = session.get(order_url)
        content = response.content.decode('gb2312', errors='replace')

        print("查询菜品通信状态代码", response.status_code)
        # 通信状态码不为200
        if response.status_code != 200:
            # 延时1秒
            time.sleep(1)
            if attempt == retries - 1:
                print("查询菜品时服务器无响应")
                return "查询菜品时服务器无响应", None, None
            continue
        else:
            break

    # 解析html
    send_bytes = BeautifulSoup(content, "html.parser")
    # 调用点餐界面解析程序
    results = order_decode(send_bytes)

    #######################################################################################
    # 下面是解析字符串并发送URL并返回包含订餐信息的文字
    #######################################################################################

    # 初始化空字典，用于存储不同餐次的菜品信息
    ordered_meals_by_type = {}

    # 初始化列表，用于存储提取的菜品id
    item_ids = []

    # 解析results并根据order_tuple中的指示提取菜品
    for meal in results:
        meal_type = meal['大餐次'][-2:]  # 从大餐次字段中提取餐别
        spicy = order_tuple[-1]  # 是否吃辣

        if meal_type == "早餐" and order_tuple[0]:
            for dish_info in meal['菜品信息']:
                for dish in dish_info['菜品']:
                    dish_name, dish_link = dish.split('：')
                    if "早餐" not in ordered_meals_by_type:
                        ordered_meals_by_type["早餐"] = []
                    ordered_meals_by_type["早餐"].append(dish_name)  # 仅添加菜名
                    if dish_link.strip() != '[无法订餐]':  # 检查链接内容
                        # print(dish_name, dish_link)  # 打印链接
                        clean_link = dish_link.strip('[]')
                        # 发送选餐链接
                        r_err = order_select(cookies, clean_link)
                        # 提取id并添加到item_ids列表
                        item_id = re.search(r'id=(\d+)_', dish_link).group(1)
                        item_ids.append(item_id)

        elif meal_type == "中餐":
            if order_tuple[1]:  # 订中餐
                for dish_info in meal['菜品信息']:
                    if dish_info['类型'] in ['主荤', '副荤']:
                        dishes = [dish for dish in dish_info['菜品'] if
                                  bool(re.search(r'.*(\(辣\)|（辣）)', dish.split('：')[0])) == spicy]
                        if "中餐" not in ordered_meals_by_type:
                            ordered_meals_by_type["中餐"] = []
                        if dishes:
                            dish_name, dish_link = dishes[0].split('：')
                            ordered_meals_by_type["中餐"].append(dish_name)
                            if dish_link.strip() != '[无法订餐]':
                                # print(dish_name, dish_link)  # 打印链接
                                clean_link = dish_link.strip('[]')
                                # 发送选餐链接
                                r_err = order_select(cookies, clean_link)
                                # 提取id并添加到item_ids列表
                                item_id = re.search(r'id=(\d+)_', dish_link).group(1)
                                item_ids.append(item_id)
                        else:
                            dish_name, dish_link = dish_info['菜品'][0].split('：')
                            ordered_meals_by_type["中餐"].append(dish_name)
                            if dish_link.strip() != '[无法订餐]':
                                # print(dish_name, dish_link)  # 打印链接
                                clean_link = dish_link.strip('[]')
                                # 发送选餐链接
                                r_err = order_select(cookies, clean_link)
                                # 提取id并添加到item_ids列表
                                item_id = re.search(r'id=(\d+)_', dish_link).group(1)
                                item_ids.append(item_id)

            if order_tuple[2]:  # 中餐加餐
                for dish_info in meal['菜品信息']:
                    if dish_info['类型'] == '加餐':
                        if "中餐" not in ordered_meals_by_type:
                            ordered_meals_by_type["中餐"] = []
                        dish_name, dish_link = dish_info['菜品'][0].split('：')
                        ordered_meals_by_type["中餐"].append(dish_name)
                        if dish_link.strip() != '[无法订餐]':
                            # print(dish_name, dish_link)  # 打印链接
                            clean_link = dish_link.strip('[]')
                            # 发送选餐链接
                            r_err = order_select(cookies, clean_link)
                            # 提取id并添加到item_ids列表
                            item_id = re.search(r'id=(\d+)_', dish_link).group(1)
                            item_ids.append(item_id)
                        break

        elif meal_type == "晚餐":
            if order_tuple[3]:  # 订晚餐
                for dish_info in meal['菜品信息']:
                    if dish_info['类型'] in ['主荤', '副荤']:
                        dishes = [dish for dish in dish_info['菜品'] if
                                  bool(re.search(r'.*(\(辣\)|（辣）)', dish.split('：')[0])) == spicy]
                        if "晚餐" not in ordered_meals_by_type:
                            ordered_meals_by_type["晚餐"] = []
                        if dishes:
                            dish_name, dish_link = dishes[0].split('：')
                            ordered_meals_by_type["晚餐"].append(dish_name)
                            if dish_link.strip() != '[无法订餐]':
                                # print(dish_name, dish_link)  # 打印链接
                                clean_link = dish_link.strip('[]')
                                # 发送选餐链接
                                r_err = order_select(cookies, clean_link)
                                # 提取id并添加到item_ids列表
                                item_id = re.search(r'id=(\d+)_', dish_link).group(1)
                                item_ids.append(item_id)
                        else:
                            dish_name, dish_link = dish_info['菜品'][0].split('：')
                            ordered_meals_by_type["晚餐"].append(dish_name)
                            if dish_link.strip() != '[无法订餐]':
                                # print(dish_name, dish_link)  # 打印链接
                                clean_link = dish_link.strip('[]')
                                # 发送选餐链接
                                r_err = order_select(cookies, clean_link)
                                # 提取id并添加到item_ids列表
                                item_id = re.search(r'id=(\d+)_', dish_link).group(1)
                                item_ids.append(item_id)

            if order_tuple[4]:  # 晚餐加餐
                for dish_info in meal['菜品信息']:
                    if dish_info['类型'] == '加餐':
                        if "晚餐" not in ordered_meals_by_type:
                            ordered_meals_by_type["晚餐"] = []
                        dish_name, dish_link = dish_info['菜品'][0].split('：')
                        ordered_meals_by_type["晚餐"].append(dish_name)
                        if dish_link.strip() != '[无法订餐]':
                            # print(dish_name, dish_link)  # 打印链接
                            clean_link = dish_link.strip('[]')
                            # 发送选餐链接
                            r_err = order_select(cookies, clean_link)
                            # 提取id并添加到item_ids列表
                            item_id = re.search(r'id=(\d+)_', dish_link).group(1)
                            item_ids.append(item_id)
                        break


    # 构建购物车表单数据，包括表单字符，提取本订单价格，当前余额。
    if len(item_ids) > 0:

        # 创建order_data列表并填充数据
        order_data = []
        if not r_err:
            for meal_type, meals in ordered_meals_by_type.items():
                order_data.append(meal_type)
                for meal in meals:
                    order_data.append(meal)

            # 打印order_data列表，记录菜名菜单
            print(order_data)
        else:
            print(f"选择菜品时出现错误：{r_err}")
            return f"选择菜品时出现错误：{r_err}", None, None

        # 构建请求的URL
        order_url = f"http://脱敏改写-请自行填写:99/wxdc/ShopCart3.asp"
        headers = {'User-Agent': user_agent}
        session = requests.session()
        session.headers = headers
        session.referer = f"http://脱敏改写-请自行填写:99/wxdc/shop3.asp?shopid=0&gtype=&dt2={formatted_date}"  # 绕过防盗链
        session.cookies = requests.cookies.cookiejar_from_dict(cookies)

        # 发起请求
        response = session.get(order_url)
        content = response.content.decode('gb2312', errors='replace')

        send_bytes = BeautifulSoup(content, "html.parser")

        # 找到包含需要的信息的<p>标签
        p_tag = send_bytes.find("p", align="center", style="height:40px;")

        # 确保找到了包含信息的<p>标签
        if p_tag:
            # 提取input标签的id和value
            input_tag = p_tag.find("input", id="ddhjje")
            if input_tag:
                input_id = input_tag['id']
                input_value = input_tag['value']
            else:
                input_id = "未找到ID"
                input_value = "未找到Value"

            # 使用正则表达式匹配余额中的金额
            balance_text = p_tag.get_text()  # 获取文本内容
            balance_amount = re.search(r"余额￥(-?\d+)", balance_text)
            if balance_amount:
                balance_amount = balance_amount.group(1)  # 提取匹配的数字部分
            else:
                balance_amount = "未找到金额"
        else:
            input_id = "未找到<p>标签"
            input_value = "未找到<p>标签"
            balance_amount = "未找到<p>标签"

        if input_id != "未找到ID" and input_id != "未找到<p>标签":

            # 输出所有提取的信息
            # print(f"ID: {input_id}, Value: {input_value}, 提取的金额：{balance_amount}")

            # 构建提交购物车请求头
            # 创建会话对象
            session = requests.session()
            session.headers = {'User-Agent': user_agent}

            # 这里正确设置referer，应当是session.headers['Referer']
            session.headers['Referer'] = "http://脱敏改写-请自行填写:99/wxdc/ShopCart3.asp"

            # 设置cookies
            session.cookies = requests.cookies.cookiejar_from_dict(cookies)

            # 构建包含多个相同键的数据字典
            data = [('ItemID', item_id) for item_id in item_ids]
            data.append((input_id, input_value))

            # 准备请求而不是直接发送，可以查看要发送的数据
            req = requests.Request('POST', "http://脱敏改写-请自行填写:99/wxdc/OrderList3.asp?action=saveorder", data=data)
            prepared = session.prepare_request(req)
            print("Prepared body:", prepared.body)

            # 发送请求
            response = session.send(prepared)
            # print(response.text)

            # 程序成功执行，返回信息与菜品列表与余额
            amount = int(balance_amount) - int(input_value)
            return "", order_data, amount

        else:

            print(input_id)
            return f"{input_id}", None, None
            pass

    else:
        print("本次无可订餐项目")
        return f"本次无可订餐项目", None, None


# 点餐界面解析程序
def order_decode(send_bytes):
    # 找到所有大餐次数据
    meal_times = send_bytes.find_all("td", bgcolor="#B1D6F3")

    # 用于存储最终结果的字典
    results = []

    # 处理每一个大餐次
    for i in range(len(meal_times)):
        meal_info = {"大餐次": meal_times[i].strong.get_text().strip()}
        dishes_info = []

        # 获取当前大餐次的范围到下一个大餐次的范围
        start = meal_times[i].parent
        if i + 1 < len(meal_times):
            end = meal_times[i + 1].parent
        else:
            # 获取整个文档的最后一个元素
            last_element = send_bytes.find_all("tr")[-1]
            end = last_element

        # 获取 end 元素的绝对位置
        end_line = end.sourceline
        end_pos = end.sourcepos

        # 获取当前大餐次和下一个大餐次之间的所有元素
        sibling_trs = []
        current = start
        passed_end = False  # 用于标记是否已经超过end元素

        while current and not passed_end:
            # 搜索所有后续的<span>元素，直到遇到end
            found_spans = current.find_all("span", style=lambda value: "color:#FF6a19" in value if value else False)
            for span in found_spans:
                # 获取 parent_tr 元素的绝对位置
                span_line = span.sourceline
                span_pos = span.sourcepos

                # 检查是否已经达到或超过 end 标记
                if span_line > end_line or (span_line == end_line and span_pos >= end_pos):
                    passed_end = True
                    break
                # 获取该span的父级<tr>
                parent_tr_span = span.find_parent("tr")
                # 获取该parent_tr_span的父级<tr>
                parent_tr = parent_tr_span.find_parent("tr")

                if parent_tr:
                    sibling_trs.append(parent_tr)
                    # 同时添加该<tr>的同级<tr>
                    next_sibling = parent_tr.find_next_sibling("tr")
                    while next_sibling:
                        sibling_trs.append(next_sibling)
                        next_sibling = next_sibling.find_next_sibling("tr")

                    # 上述程序成功后，前进一个tr元素
                    current = current.find_next("tr")

            # 移动到下一个可能的tr元素进行检查
            current = current.find_next("tr")

        for dish_type in sibling_trs:
            type_name_tag = dish_type.find("span", style=lambda value: "color:#FF6a19" in value)
            if not type_name_tag:
                continue
            type_name = type_name_tag.get_text().strip()
            dish_list = []

            # 在菜品类型下找到所有菜品
            dishes = dish_type.find_next_sibling("tr")
            if dishes:
                for dish in dishes.find_all("tr"):
                    dish_name_tag = dish.find("span", style=lambda value: "font-size:12px" in value)
                    if dish_name_tag:
                        dish_name = dish_name_tag.get_text().strip() if dish_name_tag else "未知菜品"
                        if dish_name != "未知菜品":
                            # 如果不存在已限制订餐，找iframe获取src
                            booking_info = dish.find("iframe")['src'] if dish.find("iframe") else "无法订餐"
                            if "id" in booking_info:
                                booking_info = '/' + booking_info.split('/')[
                                    1] if '/' in booking_info else booking_info

                        dish_list.append(f"{dish_name}：[{booking_info}]")
            dishes_info.append({"类型": type_name, "菜品": dish_list})

        meal_info["菜品信息"] = dishes_info
        results.append(meal_info)
    # print(results, "\n\n\n")
    """
        print(results, "\n\n\n")
        # 打印最终结果
        for result in results:
            print(f"大餐次：{result['大餐次']}")
            for dish in result['菜品信息']:
                print(f"类型：{dish['类型']}")
                print("菜品：", ", ".join(dish['菜品']))
            print()

        return results
    """
    return results


# 发送订餐选择链接，模拟点选餐品
def order_select(cookies, dish_link):
    pass
    # 重试次数
    retries = 2
    for attempt in range(retries):
        # 构建请求的URL
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) 脱敏改写-请自行填写"
        order_url = f"http://脱敏改写-请自行填写:99{dish_link}&sl=1"
        headers = {'User-Agent': user_agent}
        session = requests.session()
        session.headers = headers
        session.referer = f"http://脱敏改写-请自行填写:99{dish_link}"  # 绕过防盗链
        session.cookies = requests.cookies.cookiejar_from_dict(cookies)

        # 发起请求
        response = session.get(order_url)
        print("发送选餐url", order_url)
        print("选餐通信状态代码", response.status_code)
        # 通信状态码不为200
        if response.status_code != 200:
            # 延时1秒
            time.sleep(1)
            if attempt == retries - 1:
                print("选餐时服务器无响应")
                return "选餐时服务器无响应"
            continue
        break
    # 延时1秒
    time.sleep(0.2)


# DDDDOCR项目验证码识别
def d_ocr(img_bytes):
    ocr_1 = ddddocr.DdddOcr(show_ad=False)
    # ocr_1 = ddddocr.DdddOcr(show_ad=False, beta=True)  # 切换为第二套ocr模型
    ocr_1.set_ranges("0123456789")
    result = ocr_1.classification(img_bytes, probability=True)
    s = ""
    for i in result['probability']:
        s += result['charsets'][i.index(max(i))]
    # print(f"模型1：", s)
    # 检查结果长度是否为4
    if len(s) != 4:
        s = ""

    return s


# 专门启动主程序，方便整个程序重试调用
def food_main(control_number, u_id, u_password, u_cookie, cookie_time, days, ordering_set=()):


    # 如果操作编号等于1，则为登录验证
    if control_number == 1:
        # 重试次数
        retries = 5
        # 账号登录大循环重试
        for attempt in range(retries):
            # 调用登录函数
            login_err, cookie_dict, user_agent, u_cookie, cookie_time = account_login(u_id, u_password, u_cookie,
                                                                                      cookie_time)
            print(cookie_dict)
            if login_err == "":
                return "", "登录成功", u_cookie, cookie_time
            else:
                # 延时1秒
                time.sleep(1)

                if attempt == retries - 1:
                    return f"{login_err},重试到达最大次数。", "", u_cookie, cookie_time

    # 如果操作编号等于2，则为查询订餐
    if control_number == 2:
        # 重试次数
        retries = 5
        # 查询订单大循环重试
        for attempt in range(retries):

            # 调用登录函数
            login_err, cookie_dict, user_agent, u_cookie, cookie_time = account_login(u_id, u_password, u_cookie,
                                                                                      cookie_time)
            print(f"本次登录时使用的COOKIE{cookie_dict}")
            if login_err == "":

                # 调用查询订餐函数
                err, results = query_orders_1(login_err, cookie_dict, user_agent, days)

                # 如果没有错误信息
                if err == "":
                    # 登录成功操作,返回已订餐文本
                    return "", results, u_cookie, cookie_time

                else:
                    # 延时1秒
                    time.sleep(1)

                    if attempt == retries - 1:
                        return f"{err},重试到达最大次数。", None, u_cookie, cookie_time

            else:
                # 延时1秒
                time.sleep(1)

                if attempt == retries - 1:
                    return f"{login_err},重试到达最大次数。", "", u_cookie, cookie_time

    # 如果操作编号等于3为订餐明天，4为自动订餐调用
    if control_number == 3 or control_number == 4:
        # 重试次数
        retries = 5
        # 查询订单大循环重试
        for attempt in range(retries):

            # 调用登录函数
            login_err, cookie_dict, user_agent, u_cookie, cookie_time = account_login(u_id, u_password, u_cookie,
                                                                                      cookie_time)
            print(cookie_dict)

            if login_err == "":

                # 将订餐设置传参给筛选函数进行选择判断
                ordering_settings = orders_rules(ordering_set, control_number)

                if isinstance(ordering_settings, str):

                    return f"订餐设置：{ordering_settings}", None, u_cookie, cookie_time

                # 调用订餐函数
                err, results, amount = Order_food(cookie_dict, user_agent, ordering_settings)

                # 如果没有错误信息
                if err == "" or err == "本次无可订餐项目":

                    if results:
                        # 订餐明天操作完成,返回已订餐菜单,当前余额，cookie和生成时间
                        return "", amount, u_cookie, cookie_time
                    else:
                        return f"本次无可订餐项目。", None, u_cookie, cookie_time

                else:
                    # 延时1秒
                    time.sleep(1)

                    if attempt == retries - 1:
                        return f"{err}。重试到达最大次数。", None, u_cookie, cookie_time

            else:
                # 延时1秒
                time.sleep(1)

                if attempt == retries - 1:
                    return f"{login_err}。重试到达最大次数。", None, u_cookie, cookie_time


# 主程序执行时调用
if __name__ == "__main__":

    # 订餐查询天数
    days = 3
    # 操作编号
    control_number = 2
    u_id = "88888"
    u_password = "xxxxxx"
    u_cookie = ""
    cookie_time = ""

    err, results, u_cookie, cookie_time = food_main(control_number, u_id, u_password, u_cookie, cookie_time, days)
    if err == "":
        print(u_cookie)
        print(cookie_time)
        for result in results:
            print(result)
    else:
        print(err)
