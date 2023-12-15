import os
import json
from .tool import Tool


class QueryOrders(Tool):
    description = "用于查询车票订单。"
    description += "当用户提供完个人信息后，请立即调用该工具。"
    description += "查询成功后，请告诉用户订票人，车次，出发日期，出发站，到达站，开车时间，到达时间，座位类型，车厢号，座位号。"
    description += """
    下面是一个简单的对话场景：
    <用户>: 帮我查询一下我的订票信息
    <助手>: 正在为您调用接口...
    """
    name = "query_orders"
    # 需要的参数
    parameters: list = [
        # {
        #     "name": "passengers_name",
        #     "description": "乘车人姓名。",
        #     "required": False,
        # },
    ]
    
    def __call__(self, remote=False, *args, **kwargs):
        if self.is_remote_tool or remote:
            return self._remote_call(*args, **kwargs)
        else:
            return self._local_call(*args, **kwargs)

    def _remote_call(self, *args, **kwargs):
        pass

    def _local_call(self, *args, **kwargs):
        uuid_str = kwargs["uuid_str"]
        print("uuid str", uuid_str)
        default_agent_dir = '/tmp/agentfabric'
        default_builder_config_dir = os.path.join(default_agent_dir, 'config')
        model_cfg_file = os.getenv('BUILDER_CONFIG_DIR',
                                   default_builder_config_dir)
        uuid_dir = os.path.join(model_cfg_file, uuid_str)
        print("uuid_dir", uuid_dir)
        order_path = os.path.join(uuid_dir, "order.json")
        if os.path.exists(order_path):
            with open(order_path, "rt", encoding="utf-8") as f:
                order_list = json.load(f)
        else:
            result = "没有查询到你的订单。"
            return {"result": result}
        # passengers_name = kwargs.get("passengers_name", "")
        # if len(passengers_name) > 0:
        #     order_list = [
        #         temp for temp in order_list
        #         if temp["passengers_name"] == passengers_name
        #     ]
        return {"result": order_list}