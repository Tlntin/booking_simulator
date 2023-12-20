---
# 详细文档见https://modelscope.cn/docs/%E5%88%9B%E7%A9%BA%E9%97%B4%E5%8D%A1%E7%89%87
domain: #领域：cv/nlp/audio/multi-modal/AutoML
- multi-modal
tags: #自定义标签
  - agent
  - AgentFabric

## 启动文件(若SDK为Gradio/Streamlit，默认为app.py, 若为Static HTML, 默认为index.html)
deployspec:
  entry_file: app.py

license: Apache License 2.0
---

<h1> A "Ticket Booking Simulator" developed based on Agent</h1>
<p>Also known as "Train Travel Assistant"</p>

<p align="center">
    <br>
    <img src="./img/bg.png" width="600"/>
    <br>
<p>

<p align="center">
<a href="https://www.modelscope.cn/studios/Tlntin/booking_simulator/summary">Demo</a>
<br>
        <a href="README.md">中文</a>&nbsp ｜ &nbspEnglish
</p>


## introduce

**Ticket booking simulator** is an interactive agent framework developed based on [modelscope-agent](https://github.com/modelscope/modelscope-agent). All data are simulated, including train numbers, fares, etc. It is mainly used to simulate the scenarios that users will encounter when using AI assistants to purchase tickets, such as checking tickets, purchasing tickets, querying orders, canceling orders and other operations. Moreover, it can also distinguish between ordinary trains and high-speed trains, and know that different types of trains have different seat types and prices. If a refund occurs, a certain handling fee will be charged based on the train's departure time.

- **⚡ Ticket query**: Get the departure date, departure station, arrival station, and train type information by chatting with the user. Note: The departure date can be a relative date. By injecting the current date into the prompt, the Agent can automatically infer the absolute date representation of the user's relative date.
- **⚡ Ticket ordering**: Users need to provide the train number and seat type (such as first class/second class/business class on high-speed rail) in the chat, and in some cases also need to select the appropriate seat location (such as second class) Common ABCDF seats for waiting). Generally speaking, you need to check tickets before booking. In most cases, the travel date will be obtained from the date of ticket check.
- **⚡ Query order**: Each conversation will have a fixed session_uuid. After the user successfully books a ticket, the booking information will be stored in the json file corresponding to this session_uuid. If you need to obtain the order, read the json The file is returned.
- **⚡ Cancel order**: Users can choose to cancel all orders or specify to cancel an order. When canceling an order, the order will be deleted from the json file corresponding to the session_uuid above, and the user will be prompted for the handling fee to be deducted.
- **⚡ Weather Query**: Supports weather queries within the next two weeks, and supports weather queries within a time range, such as `What was the weather like in xxx place in the last two days`, and can even trigger weather queries in multiple locations. Different from the Amap weather tool that comes with the community, our API uses location retrieval + weather query, so it can support any place name search without too precise expression. And after the ticket is successfully ordered, there is a high chance that the weather at the departure station and arrival station will be automatically checked, and the user will be reminded of travel and dressing related information.
- **⚡ Data persistence**: By asynchronously and randomly generating a session_uuid before each conversation, the user can be given a temporary identity. If the user copies and stores the `session_uuid`, refreshes the page, and refills it, then You can continue to keep previous order records. Of course, it may be better to use the uuid of the real registered user here, but it is currently impossible to obtain the user uuid of modelscope, so this is the last resort.
- **⚡Exception handling**: When the api encounters an error, it will automatically trigger three retry mechanisms. If all three retries fail, the status code and error message will be returned to the input box to remind the user that the current system is abnormal, and It's not the original version that just freezes and becomes unresponsive. This kind of processing is relatively more friendly, letting users know that it is a system failure rather than a problem with their network.

🔗Supporting development tutorial: [Agent Zone - Zhihu (zhihu.com)](https://www.zhihu.com/column/c_1720569519108485120)



## Prerequisites

-Python 3.10
- Obtain the API-key required to use the Qwen 2.0 model, which can be obtained from [DashScope](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key ) is free to activate and obtain.
- To obtain the ModelScope sdk key, you can refer to the supporting development tutorial above to obtain it.
- Get the free API of Qweather, get the website: https://dev.qweather.com

## Install

Clone the repository and install dependencies:

```bash
git clone https://github.com/Tlntin/booking_simulator.git
cd booking_simulator
pip install -r requirements-dev.txt
pip install -r requirements.txt
```

## Instructions

- Environment variable import
```bash
export DASHSCOPE_API_KEY=your_api_key
export MODELSCOPE_API_TOKEN=your_token
export QWEATHER_TOKEN_FREE=your_free_token
```

- (Optional) Import environment variables, use the standard version (paid) of the Zephyr weather API, and support weather queries within 14 days.
```bash
export QWEATHER_TOKEN_PRO=your_pro_token
```

- Formal operation
```bash
python app.py
```

# project instruction

- Below is the main file description
```bash
config/ # There are many configuration files in it. The ones enabled by default are model_config.json and tool_config.json.
modelscope_agent/tools/ # The location of the registered tool chain
app.py # Startup entry, also the default file after going online, most of the modifications are made here
appBot.py # An intelligent project that creates Agent through dialogue. It is actually the original startup file of this project and is for reference only.
config_utils.py # Read the code for default configuration, modification is not recommended
custom_prompt.py # prompt is defined by default, don’t change it yet
excel2db.py # Code to convert existing online tickets excel to sqlite3 database
```

### Project experience
- Demo video: https://www.bilibili.com/video/BV1NQ4y137GX/
- Experience address: https://www.modelscope.cn/studios/Tlntin/booking_simulator/summary
