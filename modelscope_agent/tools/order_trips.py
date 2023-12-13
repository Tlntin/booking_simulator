import datetime
import random

from .tool import Tool
import sqlite3


class OrderTrips(Tool):
    description = "用于订购车票。"
    description += "当用户提供完所有订票相关信息后，请立即调用该工具。"
    description += "需要先完成车票查询任务，才能订购车票。"
    description += "如果用户直接订购车票，先帮他查一下车票"
    description += """
    下面是一个简单的对话场景：
    <用户>: 帮我订购明天的，G32车次的，二等座
    <客服>：好的，请问乘车人是？
    <用户>: 张三
    """
    name = "order_trips"
    # 需要的参数
    parameters: list = [
        {
            "name": "date",
            "description": "出发日期",
            "required": True,
        },
        {
            "name": "train_code",
            "description": "火车编号/车次",
            "required": True,
        },
        {
            "name": "trips_type",
            "description": "车票类型：二等座/一等座/商务座/无座/硬座/硬卧/软卧",
            "required": True,
        },
        {
            "name": "passengers_name",
            "description": "乘车人姓名。",
            "required": True,
        },
        {
            "name": "passengers_idcard",
            "description": "乘车人身份证号码（可选），如果填写则必须是13位数字，最后一位可以为字母X",
            "required": False,
        }
    ]

    def __call__(self, remote=False, *args, **kwargs):
        if self.is_remote_tool or remote:
            return self._remote_call(*args, **kwargs)
        else:
            return self._local_call(*args, **kwargs)

    def _remote_call(self, *args, **kwargs):
        pass

    @staticmethod
    def find_trips(cursor, name: str):
        """
        :param cursor:
        :param name: station name
        :return:
        """
        sql = f'SELECT x.name FROM station x where name like "%{name}%"'
        cursor.execute(sql)
        data = cursor.fetchall()
        station_list = [da[0] for da in data]
        return station_list

    def _local_call(self, *args, **kwargs):
        date = kwargs['date']
        now_date = datetime.datetime.now().strftime("%Y-%m-%d")
        train_code = kwargs["train_code"]
        station_to = kwargs["trips_type"]
        passengers_name = kwargs["passengers_name"]
        passengers_idcard = kwargs.get("passengers_idcard", None)
        print("db_path", self.db_path)
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        if date <= now_date:
            result = f"无法订购日期为{date}的车票，时间非法"
            return {"result": result}

