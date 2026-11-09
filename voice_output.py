# 接受来自大模型输出的结果res
# visit_seq = [["des1","des2","des3","des4","des5"],[["des1","des2"],["des3","des4"],["des5"]]]
#      一共去了5个景点，其中第一天去了1，2，第二天去了3,4，第三天去了5
#     景点名称例如"故宫","长城"等
# res = [args, reply, visit_seq]

# encoding: utf-8
import uuid
import time
import requests
import os
from auth_util import gen_sign_headers
import pyttsx3
from get_ai import llm_information

# 从change.py这个python文件中调用llm_information()这个函数
# 请替换APP_ID、APP_KEY
APP_ID = os.environ.get('VIVO_APP_ID', '')
APP_KEY = os.environ.get('VIVO_APP_KEY', '')
URI = '/vivogpt/completions'
DOMAIN = 'api-ai.vivo.com.cn'
METHOD = 'POST'
# 接受来自大模型输出的结果res
# visit_seq = [["des1","des2","des3","des4","des5"],[["des1","des2"],["des3","des4"],["des5"]]]
#      一共去了5个景点，其中第一天去了1，2，第二天去了3,4，第三天去了5
#     景点名称例如"故宫","长城"等
# res = [args, reply, visit_seq]


def output_voice(res):
    # 调用语音API，并且播放声音,不需要返回值
    params = {
        'requestId': str(uuid.uuid4())
    }
    print('requestId:', params['requestId'])

    data = {
        'prompt': '我计划到'+res[0][0]+'四日游，第一天去'+res[2][1][0][0]+','+res[2][1][0][1]+','+res[2][1][0][2]+'，第二天去'+res[2][1][1][0]+','+res[2][1][1][1]+','+res[2][1][1][2]+'，第三天去'+res[2][1][2][0]+','+res[2][1][2][1]+','+res[2][1][2][2]+'，第四天去'+res[2][1][3][0]+','+res[2][1][3][1]+','+res[2][1][3][2]+'请用一段话介绍这段旅程，要求引经据典，具有文学色彩',
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
    print("get respone for voice out!")
    if response.status_code == 200:
        res_obj = response.json()
        print(f'response:{res_obj}')
        if res_obj['code'] == 0 and res_obj.get('data'):
            content = res_obj['data']['content']
            # 初始化
            engine = pyttsx3.init()

            # 设置语音速率
            engine.setProperty('rate', 150)

            # 设置语音
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)  # 0 for male voice, 1 for female voice

            # 输入文本
            engine.say(content)

            # 播放
            engine.runAndWait()
            print(f'final content:\n{content}')
    else:
        print(response.status_code, response.text)
    end_time = time.time()
    timecost = end_time - start_time
    print('请求耗时: %.2f秒' % timecost)

# 示例数据
# args = ["北京","2024/5/1","2024/5/4",0,1,["想去故宫","更加便捷的交通方式"]]
# res = llm_information(args)
# output_voice(res)
