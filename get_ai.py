# encoding: utf-8
import uuid
import re
import time
import requests
import os
from auth_util import gen_sign_headers

# 请替换APP_ID、APP_KEY
APP_ID = os.environ.get('VIVO_APP_ID', '')
APP_KEY = os.environ.get('VIVO_APP_KEY', '')
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'
# 示例数据
# args = ["北京","2024/5/1","2024/5/4",0,1,["想去故宫","更加便捷的交通方式"]]
def llm_information(args):
    print(args)
    # 先将接受的参数列表存储到变量中
    destination = args[0]
    start_date = args[1]
    end_date = args[2]
    budget = args[3]
    partner = args[4]
    keyword = args[5]

    # 验证数据是否完整
    # if destination  or start_date or end_date or budget or  partner  or keyword is None:
    #   return {'error': '缺少必要参数'}
    if len(keyword) > 5:
        return {"error": "关键词列表长度不能超过5"}
    # 提取数据
    # 根据预算转换
    budget_ranges = {
        0: "0-1000元",
        1: "1000-5000元",
        2: "5000元以上"
    }
    budget_text = budget_ranges.get(budget)

    # 根据同行人转换
    partner_options = {
        0: "一个人去",
        1: "和朋友一起去",
        2: "和家人一起去",
        3: "情侣出行"
    }
    partner_text = partner_options.get(partner)
    keywords =""
    for i in range (len(keyword)+1) :
        keywords += keyword[i-1]
    # 与大模型交互，并且经过处理后按照指定格式输出
    def sync_vivogpt():
        params = {
            'requestId': str(uuid.uuid4())
        }
        print('requestId:', params['requestId'])

        data = {
            'prompt': '请提供一份详细的' +
                      destination +
                      '只包括第几天和地点，其中每天2个景点。' +
                      '我的预算在' +
                      budget_text +
                      '，开始时间是' +
                      start_date +
                      '，结束时间是' +
                      end_date +
                      '，我' +
                      partner_text +
                      '，我的个性化需求是' +
                      keywords +
                      '。请确保行程清晰、连贯，并且符合我的预算范围。同时，请避免提供任何可能产生安全隐患的建议,每天只去两个景点。该旅行计划的输出格式必须为day1，第一天要去的景点，day2，第二天要去的景点。' +
                      '请仿照下列我给你的这个标准案例格式进行生成，标准案例的格式如下day1：广州塔，广东省博物馆，珠江夜游day2：白云山，上下九步行街，陈家祠day3：长隆野生动物园，天河购物中心，珠江新城day4：越秀公园，南越王宫博物馆，北京路步行街' +
                      '请注意内容只包括第几天和地点，不要有其他话。',
            'model': 'vivo-BlueLM-TB',
            'sessionId': str(uuid.uuid4()),
            'extra': {
                'temperature': 0.9
            }
        }
        headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
        headers['Content-Type'] = 'application/json'

        start_time = time.time()
        url = 'https://{}{}'.format(DOMAIN, URI)
        response = requests.post(url, json=data, headers=headers, params=params)

        content = ""

        if response.status_code == 200:
            res_obj = response.json()
            print(f'response:{res_obj}')
            if res_obj['code'] == 0 and res_obj.get('data'):
                content = res_obj['data']['content']
                print(f'final content:\n{content}')
        else:
            print(response.status_code, response.text)
        end_time = time.time()
        timecost = end_time - start_time
        print('请求耗时: %.2f秒' % timecost)

        return content

    # 此变量存储模型输出的完整旅游攻略文字
    reply = sync_vivogpt()
    # 文本处理
    # 去除换行符
    reply = reply.replace('\n',' ').replace('\r',' ')
    sentence = re.findall(r"day1：(.*)day2：(.*)day3：(.*)day4：(.*)", reply)[0]
    # print(sentence)

    V1 = [sentence[0]]
    V2 = [sentence[1]]
    V3 = [sentence[2]]
    V4 = [sentence[3]]
    # 使用split()方法分割字符串,items[0].split(',')
    visit_seq =[ [V1+ V2+ V3+ V4],[ V1[0].split('，'),V2[0].split('，'),V3[0].split('，'),V4[0].split('，')]] # 这是一个多维列表，第一个列表记录所有景点的名字。第二个列表按照天归类景点
    # visit_seq = [["des1","des2","des3","des4","des5"],[["des1","des2"],["des3","des4"],["des5"]]]
    # 一共去了5个景点，其中第一天去了1，2，第二天去了3,4，第三天去了5
    # 景点名称例如"故宫","长城"等
    res = [args, reply, visit_seq]
    return res

def des_information(res):
    intro_result = []
    # 先将接受的参数列表存储到变量中
    visit_seq = res[2]
    print(visit_seq)
    for des_list in visit_seq:
        def sync_vivogpt(des):
            params = {
                'requestId': str(uuid.uuid4())
            }
            print('requestId:', params['requestId'])

            data = {
                'prompt': "请用一段话介绍一下旅游景点"+des+"你的输出应该只包含介绍的内容，不要有其他话。",
                'model': 'vivo-BlueLM-TB',
                'sessionId': str(uuid.uuid4()),
                'extra': {
                    'temperature': 0.9
                }
            }
            headers = gen_sign_headers(APP_ID, APP_KEY, METHOD, URI, params)
            headers['Content-Type'] = 'application/json'

            start_time = time.time()
            url = 'https://{}{}'.format(DOMAIN, URI)
            response = requests.post(url, json=data, headers=headers, params=params)

            content = ""

            if response.status_code == 200:
                res_obj = response.json()
                print(f'response:{res_obj}')
                if res_obj['code'] == 0 and res_obj.get('data'):
                    content = res_obj['data']['content']
                    print(f'final content:\n{content}')
            else:
                print(response.status_code, response.text)
            end_time = time.time()
            timecost = end_time - start_time
            print('请求耗时: %.2f秒' % timecost)

            return content

        # 此变量存储模型输出的完整旅游攻略文字
        for des in des_list:
            reply = sync_vivogpt(des)
            reply = reply.replace('\n',' ').replace('\r',' ')
            intro_result.append([des,reply])
    # print(sentence)
    return intro_result
