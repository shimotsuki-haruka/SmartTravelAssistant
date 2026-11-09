import eel
import get_ai
import voice_output
import weather

eel.init("Web")
# 用于存储大模型返回值的全局变量
result = []
destination_result = []
weather_flag = True
weather_result = []
# 处理大模型输出的结果，转换成html需要的格式
# 暴露给test_output.html使用

@eel.expose
def get_weather_result():
    global weather_flag,weather_result
    return weather_flag,weather_result
    
@eel.expose
def get_process_result():
    global destination_result
    print(destination_result)
    print(destination_result[0][0])
    return destination_result


def process_result():
    global result,destination_result
    destination_result = get_ai.des_information(result)
    

@eel.expose
def voice_out():
    print("start voice out!")
    print(result)
    voice_output.output_voice(result)
    print("voice out finish")


# 暴露给html的函数
@eel.expose
def get_result(input_array):
    global result
    print(input_array)
    result = get_ai.llm_information(input_array)
    weather_flag,weather_result = weather.get_weather(input_array)
    process_result()
    # eel.start("test_output.html",port=0,size=(600,300),mode='egde')
    


eel.start('main.html', port=0, size=(600,300),mode="edge")