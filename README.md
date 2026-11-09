# 智旅家 SmartTravelAssistant

智旅家是一个基于 Python Eel 的桌面式旅游规划演示项目。用户输入目的地、出行日期、预算区间、同行人和偏好关键词后，程序调用 vivo 蓝心大模型生成行程建议，并结合高德天气和地图服务展示结果。项目名称与产品思路来自原有的 DOCX 策划书和 PPT 演示稿；以下功能说明以仓库中的代码为准。

## 当前功能

- 根据目的地、日期、预算区间、同行人及最多 5 个偏好关键词生成旅行行程。
- 查询目的地的高德天气预报，并在结果页展示。
- 在结果页使用高德地图展示地点和公交换乘信息。
- 生成景点介绍，并使用本机语音引擎播报行程介绍。

策划文档中提到的机票和酒店预订、精确预算汇总、语音输入以及通过对话修改行程，目前没有完整实现。当前行程解析和语音播报按四天的输出格式编写，其他天数可能无法正常工作；天气预报也只覆盖高德服务可提供的日期。

## 技术组成

- Python：Eel、Requests、Pandas、OpenPyXL、pyttsx3
- 前端：HTML、CSS、JavaScript
- 外部服务：vivo 蓝心大模型、高德天气与地图 API
- 数据：`adcode_citycode.xlsx` 用于城市名称与 adcode 对应

## 本地运行

1. 安装 Python 3.12 或兼容版本，以及 Microsoft Edge。
2. 在项目根目录安装依赖：

   ```powershell
   python -m pip install eel requests pandas openpyxl pyttsx3
   ```

3. 配置自己的服务凭据。PowerShell 示例：

   ```powershell
   $env:VIVO_APP_ID = 'your-vivo-app-id'
   $env:VIVO_APP_KEY = 'your-vivo-app-key'
   $env:AMAP_WEB_SERVICE_KEY = 'your-amap-web-service-key'
   Copy-Item Web/config.example.js Web/config.js
   ```

   然后编辑 `Web/config.js`，填写 `STA_AMAP_WEB_KEY` 和 `STA_AMAP_SECURITY_CODE`。该文件已加入 `.gitignore`。高德浏览器端凭据会随地图请求发送到浏览器，应在高德控制台设置允许使用的域名等限制；不要在此填写服务端密钥。

4. 启动程序：

   ```powershell
   python main.py
   ```

程序从 `Web/main.html` 打开。点击“现在开始”进入输入页；地图和行程结果由 `Web/test_output.html` 展示。外部服务调用需要有效凭据和网络连接。

## 项目结构

| 路径 | 用途 |
| --- | --- |
| `main.py` | 初始化 Eel，连接页面与 Python 功能 |
| `get_ai.py` | 请求大模型并处理行程、景点介绍 |
| `weather.py` | 查询城市天气预报 |
| `voice_output.py` | 生成并播报行程介绍 |
| `auth_util.py` | vivo API 请求签名 |
| `Web/` | 页面、样式、脚本与图片资源 |
| `adcode_citycode.xlsx` | 城市编码数据 |

## 安全与资料说明

仓库不包含本地凭据配置及开发环境缓存。原源码曾包含外部服务凭据；如果这些凭据仍然有效，应在对应服务平台撤销并重新生成。
