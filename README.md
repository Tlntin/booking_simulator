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

<h1> Modelscope AgentFabric: 开放可定制的AI智能体构建框架</h1>

<p align="center">
    <br>
    <img src="https://modelscope.oss-cn-beijing.aliyuncs.com/modelscope.gif" width="400"/>
    <br>
<p>

## 介绍

**Modelscope AgentFabric**是一个交互式智能体框架，用于方便地创建针对各种现实应用量身定制智能体。AgentFabric围绕可插拔和可定制的LLM构建，并增强了指令执行、额外知识检索和利用外部工具的能力。AgentFabric提供的交互界面包括：
- **⚡ 智能体构建器**：一个自动指令和工具提供者，通过与用户聊天来定制用户的智能体
- **⚡ 用户智能体**：一个为用户的实际应用定制的智能体，提供构建智能体或用户输入的指令、额外知识和工具
- **⚡ 配置设置工具**：支持用户定制用户智能体的配置，并实时预览用户智能体的性能

🔗 我们目前围绕DashScope提供的 [Qwen2.0 LLM API](https://help.aliyun.com/zh/dashscope/developer-reference/api-details) 来在AgentFabric上构建不同的智能体应用。同时我们正在积极探索，通过API或者ModelScope原生模型等方式，引入不同的举办强大基础能力的LLMs，来构建丰富多样的Agents。

## 前提条件

- Python 3.10
- 获取使用Qwen 2.0模型所需的API-key，可从[DashScope](https://help.aliyun.com/zh/dashscope/developer-reference/activate-dashscope-and-create-an-api-key)免费开通和获取。

## 安装

克隆仓库并安装依赖：

```bash
git clone https://github.com/Tlntin/booking_simulator.git
cd booking_simulator
pip install -r requirements-dev.txt
pip install -r requirements.txt
```

## 使用方法

```bash
export PYTHONPATH=$PYTHONPATH:/path/to/your/modelscope-agent
export DASHSCOPE_API_KEY=your_api_key
python app.py
```

## 

# 项目说明

- 该项目参考[该教程]([modelscope Agent 新人开发教程_天池技术圈-阿里云天池 (aliyun.com)](https://tianchi.aliyun.com/forum/post/641455))创建
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

