import pandas as pd
import requests
import os
from datetime import datetime, timedelta
import re

def convert_date_format(date_str):
    """
    将日期字符串从"月/日/年"格式转换为"日/月/年"格式。

    参数:
    date_str (str): 需要转换的日期字符串，格式为"月/日/年"。

    返回:
    str: 转换后的日期字符串，格式为"日/月/年"。
    """
    # 检查输入的日期字符串是否符合"月/日/年"的格式
    parts = date_str.split('/')
    if len(parts) != 3:
        raise ValueError("日期格式不正确，应为'月/日/年'")

    # 分别获取月、日、年部分
    month, day, year = parts

    # 检查月、日、年是否都是数字
    if not (month.isdigit() and day.isdigit() and year.isdigit()):
        raise ValueError("日期中的月、日、年部分必须是数字")

    # 构造并返回新的日期格式
    new_date_str = f"{day}/{month}/{year}"
    return new_date_str

def is_date_in_range(query_date, start_date_str, end_date_str):
    # 将日期字符串转换为datetime对象
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
    # 判断查询日期是否在开始日期和结束日期之间
    return start_date <= query_date <= end_date


def days_between_dates(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    end_date = datetime.strptime(end_date_str, '%d/%m/%Y')
    delta = end_date - start_date
    return delta.days + 1  # 包含结束日期当天


# 载入城市代码文件
data = pd.read_excel('adcode_citycode.xlsx')  # 城市代码文件
city_codes = data.set_index('中文名')['adcode'].to_dict()  # 创建城市名称到编码的字典

APP_KEY = os.environ.get('AMAP_WEB_SERVICE_KEY', '')
URI = 'https://restapi.amap.com/v3/weather/weatherInfo'


def normalize_city_name(city_name):
    # 使用正则表达式去掉城市名称中的“市”、“县”、“区”等后缀
    return re.sub(r'(市|县|区)$', '', city_name)


def find_city_adcode(city_name):
    city_name_normalized = normalize_city_name(city_name)

    for name in city_codes.keys():
        if normalize_city_name(name) == city_name_normalized:
            return city_codes[name]

    return None


# args输入格式参考
# args = ["北京","07/24/2024","07/28/2024",0,1,["想去故宫","更加便捷的交通方式"]]
def get_weather(args):
    city_name = args[0]
    start_date_str = args[1]
    end_date_str = args[2]
    start_date_str = convert_date_format(start_date_str)
    end_date_str  = convert_date_format(end_date_str)
    num_days = days_between_dates(start_date_str, end_date_str)

    adcode = find_city_adcode(city_name)
    if not adcode:
        return False, ["未找到该城市的编码"]

    parameters = {
        'key': APP_KEY,
        'city': adcode,
        'extensions': 'all'
    }

    response = requests.get(URI, params=parameters)
    if response.status_code != 200:
        return False, ["天气服务请求失败"]

    data = response.json()

    if 'forecasts' not in data or not data['forecasts']:
        return False, ["未获取到天气预测数据"]

    forecasts = data['forecasts'][0]['casts']

    flag = False
    result = []

    start_date = datetime.strptime(start_date_str, '%d/%m/%Y')
    for i in range(num_days):
        forecast_date = start_date + timedelta(days=i)
        matched_forecast = next((f for f in forecasts if datetime.strptime(f['date'], '%Y-%m-%d') == forecast_date),
                                None)

        if matched_forecast:
            flag = True
            result.append(matched_forecast['dayweather'])
        else:
            result.append(None)

    return flag, result


# 示例调用
# args = ["北京", "18/07/2024", "22/07/2024", 0, 1, ["想去故宫", "更加便捷的交通方式"]]
# flag, result = get_weather(args)
# print(f"是否可以预测: {flag}")
# print(f"预测结果: {result}")
