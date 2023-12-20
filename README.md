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

<h1> 一个基于Agent开发的《订票模拟器》</h1>
<p>别称《火车出行小助手》</p>

<p align="center">
    <br>
    <img src="./img/bg.png" width="600"/>
    <br>
<p>


## 介绍

**订票模拟器**是一个交互式智能体框架，基于[modelscope-agent](https://github.com/modelscope/modelscope-agent)开发。所有数据均为模拟的，包括车次，票价等。主要用于模拟用户使用AI助手购票将会遇到的场景，查票，购票，查询订单，取消订单等操作。并且，它还能够区分普通火车和高铁，并且知道不同类型的火车有不同的座位类型和价格。如果发生退票，会根据火车开车时间，收取一定手续费。

- **⚡ 车票查询**：通过和用户聊天，得到出发日期，出发车站，到达车站，火车类型信息。注：其中出发日期可以为相对日期，通过在prompt中注入当前日期，让Agent可以自动推断用户相对日期的绝对日期表示。
- **⚡ 车票订购**：用户需要在聊天中提供车次，座位类型（比如高铁有一等座/二等座/商务座），并且在某些情况下还需要选择合适的座位位置（比如二等座常见的ABCDF座位）。一般来说，需要先查票再订票，大部分情况下，将从查票的的日期中，获取出行日期。
- **⚡ 查询订单**：每次对话都会有一个固定的session_uuid，用户订票成功后，会将订票信息储存在这个session_uuid对应的json文件中，如果需要获取订单，则读取该json文件进行返回。
- **⚡ 取消订单**：用户可以选择取消所有订单，也可以指定取消某个订单。取消订单时，将从上面的session_uuid中对应的json文件中，删除该笔订单，并提示用户扣取多少手续费。
- **⚡ 天气查询**：支持未来两周内的天气查询，并且支持时间范围内的天气查询，例如`最近两天的xxx地方的天气如何`，甚至可以触发多地点天气查询。与社区自带的高德天气tool不同，我们的api采用位置检索+天气查询，所以可以支持任意地名搜索，不用太过精准的表达。并且在车票订购成功后，有较大几率，自动查询出发站，达到站的天气，提醒用户出行与穿衣相关信息。
- **⚡ 数据持久化**：通过在每次对话前，异步随机生成一个session_uuid，可以赋予用户一个临时身份，若用户将该`session_uuid`复制储存起来，刷新页面后，重新填入，则可以继续保留之前的订单记录。当然，这里用真实注册用户的uuid或许效果会更好，只不过目前无法获取modelscope的用户uuid，所以出此下策。
- **⚡ 异常处理**：当api遇到报错时候，自动触发3次重试机制，若三次重试后均失败，则返回状态码和错误信息到输入框，提醒用户当前系统异常，而不是原版的直接卡死无响应。这样的处理相对来说更加友好，让用户知道是系统故障而不是他们网络有问题。

🔗配套开发教程：[Agent专区 - 知乎 (zhihu.com)](https://www.zhihu.com/column/c_1720569519108485120)



## 前提条件

- Python 3.10
- 获取使用Qwen 2.0模型所需的API-key，可从[DashScope](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key)免费开通和获取。
- 获取ModelScope sdk key，可以参考上面的配套开发教程获取。
- 获取和风天气的免费api，获取网站：https://dev.qweather.com

## 安装

克隆仓库并安装依赖：

```bash
git clone https://github.com/Tlntin/booking_simulator.git
cd booking_simulator
pip install -r requirements-dev.txt
pip install -r requirements.txt
```

## 使用方法

- 环境变量导入
```bash
export DASHSCOPE_API_KEY=your_api_key
export MODELSCOPE_API_TOKEN=your_token
export QWEATHER_TOKEN_FREE=your_free_token
```

- （可选）环境变量导入，使用标准版（付费的）的和风天气api，支持14天内的天气查询。
```bash
export QWEATHER_TOKEN_PRO=your_pro_token
```

- 正式运行
```bash
python app.py
```

# 项目说明

- 下面是主要文件说明
```bash
config/  # 里面有很多配置文件，默认启用的是model_config.json和tool_config.json
modelscope_agent/tools/ # 注册工具链的位置
app.py # 启动入口，也是上线后的默认文件，大部分是修改这个地方
appBot.py # 一个智能的，通过对话创建Agent的项目，其实也是这个项目的原始启动文件，仅作参考。
config_utils.py # 读取默认配置的代码，不建议修改
custom_prompt.py # prompt默认定义，暂时先别改
excel2db.py # 将网上现有车票excel转sqlite3数据库的代码
```

### 项目体验
- 演示视频：https://www.bilibili.com/video/BV1NQ4y137GX/
- 体验地址：https://www.modelscope.cn/studios/Tlntin/booking_simulator/summary
