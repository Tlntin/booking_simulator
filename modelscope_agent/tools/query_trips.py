from .tool import Tool
import sqlite3


class QueryTrips(Tool):
    description = "用于查询火车票"
    name = "query_trips"
    # 需要的参数
    parameters: list = [
        {
            "name": "date",
            "description": "出发日期",
            "required": True,
        },
        {
            "name": "station_from",
            "description": "出发车站",
            "required": True,
        },
        {
            "name": "station_to",
            "description": "到达车站",
            "required": True,
        },
        {
            "name": "trips_type",
            "description": "车票类型：<高铁>或者<普通火车>或者<都可以>",
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
        date = kwargs['date']
        station_from = kwargs["station_from"]
        station_to = kwargs["station_to"]
        tripe_type = kwargs["trips_type"]
        return f'你的出发日期是：{date}, 出发车站为：{station_from}, 到达车站为：{station_to}, 选择的车票类型是{tripe_type}'
