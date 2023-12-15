import os
import json
import datetime
from .tool import Tool
from .qweather_api import get_current_weather


class QueryWeather(Tool):
    description = "划重点：该工具用于查询地方天气。"

    name = "query_weather"
    # 需要的参数
    parameters: list = [
        {
            "name": "location",
            "description": "地点",
            "required": True,
        },
        {
            "name": "query_date",
            "description": "日期",
            "required": True,
        },
    ]

    def __call__(self, remote=False, *args, **kwargs):
        if self.is_remote_tool or remote:
            return self._remote_call(*args, **kwargs)
        else:
            return self._local_call(*args, **kwargs)

    def _remote_call(self, *args, **kwargs):
        pass

    def _local_call(self, *args, **kwargs):
        # uuid_str = kwargs["uuid_str"]
        # print("uuid str", uuid_str)
        
        location = kwargs.get("location", "")
        query_date = kwargs.get("query_date", "")
        
        if location is None or query_date is None:
            raise ValueError("location: {}, query_date{}, ValueRrror".format(location, query_date))
        
        query_date = datetime.datetime.strptime(query_date, "%Y-%m-%d")
        now_date = datetime.datetime.today()
        diff_days = (query_date.date() - now_date.date()).days
        
        if diff_days < 0:
            raise ValueError("Can't predict weather of passed dates.")
        
        if diff_days >= 3:
            return {"result": "不能预测多于2天的天气"}
        
        else:
            resp = get_current_weather(location=location)
            
            print(resp)
            for item in resp:
                if item["fxDate"] == query_date.strftime('%Y-%m-%d'):
                    return {"result": item}
        return {"result": "查不到当天的天气"} 
