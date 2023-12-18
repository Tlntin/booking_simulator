import os
import json
import datetime
from .tool import Tool
from .qweather_api import Weather
from modelscope_agent.tools.tool import Tool, ToolSchema
from pydantic import ValidationError


class QueryWeather(Tool):
    description = "划重点：该工具用于查询地方天气。"
    description += "天气查询完成后，请向用户说明出行建议与穿衣指南。"
    name = "query_weather"
    # 需要的参数
    parameters: list = [
        {
            "name": "location",
            "description": "地点",
            "required": True,
        },
        {
            "name": "start_date",
            "description": "开始日期",
            "required": True,
        },
        {
            "name": "end_date",
            "description": "结束日期",
            "required": True,
        },
    ]

    def __init__(self, cfg = {}):
        self.cfg = cfg.get(self.name, {})
        self.token_free = self.cfg.get('token', os.environ.get('QWEATHER_TOKEN_FREE', ''))
        self.token_pro = self.cfg.get('token', os.environ.get('QWEATHER_TOKEN_PRO', ''))
        assert self.token_free != '', 'weather api token must be acquired through ' \
            '"please get weather query api in https://dev.qweather.com/") \
            and set by QWEATHER_TOKEN'
        self.weather = Weather(self.token_free, self.token_pro)
        self.is_remote_tool = True
        try:
            all_param = {
                'name': self.name,
                'description': self.description,
                'parameters': self.parameters
            }
            self.tool_schema = ToolSchema(**all_param)
        except ValidationError:
            raise ValueError(f'Error when parsing parameters of {self.name}')

        self._str = self.tool_schema.model_dump_json()
        self._function = self.parse_pydantic_model_to_openai_function(
            all_param)

    def get_current_weather(self, location: str, duration: str = "7d"):
        """_summary_

        Args:
            location (str): _description_
            duration (str, optional): _description_. Defaults to "7d", can select "15d" and "7d"

        Returns:
            _type_: _description_
        """
        location_data = self.weather.get_location_from_api(location)
        if len(location_data) > 0:
            location_dict = location_data[0]
            city_id = location_dict["id"]
            weather_res = self.weather.get_weather_from_api(city_id, duration=duration)
            return weather_res
        else:
            return []

    def __call__(self, remote=False, *args, **kwargs):
        if self.is_remote_tool or remote:
            return self._remote_call(*args, **kwargs)
        else:
            return self._local_call(*args, **kwargs)

    def _local_call(self, *args, **kwargs):
        pass

    def _remote_call(self, *args, **kwargs):
        # uuid_str = kwargs["uuid_str"]
        # print("uuid str", uuid_str)
        
        location = kwargs.get("location", "")
        start_date = kwargs.get("start_date", "")
        end_date = kwargs.get("end_date", "")

        if len(location) == 0 or len(start_date + end_date) == 0:
            raise ValueError("location: {}, start_date{}, end_date{} ValueRrror".format(
                location, start_date, end_date
            ))
        elif len(start_date) > 0 and len(end_date) == 0:
            end_date = start_date
        elif len(start_date) == 0 and len(end_date) > 0:
            start_date = end_date
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
        if start_date > end_date:
            start_date, end_date = end_date, start_date
        now_date = datetime.datetime.today()
        diff_day1 = (start_date.date() - now_date.date()).days
        diff_day2 = (end_date.date() - now_date.date()).days

        if diff_day1 < 0:
            return {"result": "不能查询过去日期的天气"}
        
        if diff_day2 >= 15:
            return {"result": "只支持查询14天内的天气"}
        elif diff_day2 > 7:
            duration = "15d"
        else:
            duration = "7d"
        print("location: ", location)
        resp = self.get_current_weather(location=location, duration=duration)
        print("result", resp)
        start_date = start_date.strftime('%Y-%m-%d')
        end_date = end_date.strftime('%Y-%m-%d')
        resp = [
            item for item in resp
            if start_date <= item["date"] <= end_date
        ]
        if len(resp) > 0:
            return {"result": resp}
        else:
            return {"result": "查不到当天的天气"}
