from .tool import Tool
import random


class QueryOrders(Tool):
    description = "用于查询车票订单。"
    description += "当用户提供完个人信息后，请立即调用该工具。"
    description += """
    下面是一个简单的对话场景：
    <用户>: 帮我查询一下乘客张三的订票信息
    <助手>: 正在为您调用接口...
    """
    name = "query_orders"
    # 需要的参数
    parameters: list = [
        # {
        #     "name": "date",
        #     "description": "出发日期",
        #     "required": True,
        # },
        # {
        #     "name": "train_code",
        #     "description": "火车编号/车次",
        #     "required": True,
        # },
        {
            "name": "passengers_name",
            "description": "乘车人姓名。",
            "required": True,
        },
        # {
        #     "name": "passengers_idcard",
        #     "description": "乘车人身份证号码（可选），如果填写则必须是13位数字，最后一位可以为字母X",
        #     "required": False,
        # }
    ]
    
    def __call__(self, remote=False, *args, **kwargs):
        if self.is_remote_tool or remote:
            return self._remote_call(*args, **kwargs)
        else:
            return self._local_call(*args, **kwargs)

    def _remote_call(self, *args, **kwargs):
        pass

    def _local_call(self, *args, **kwargs):
        result_dict = {
            "code": "G88",
            "station_from": "广州南",
            "station_to": "北京西",
            "start": "10:01",
            "end": "18:01",
            "type": "高铁",
            "trips_type": "二等座",
            "price": 888,
            "carriage_number": random.randint(1, 18),
            "seat_number": random.randint(1, 24),
            "seat_type": "A",
            "passengers_name": "hello world",
            # "passengers_idcard": passengers_idcard[:6] + "*" * 6 + passengers_idcard[-4: ]
        }
        return {"result": result_dict}