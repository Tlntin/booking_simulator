import datetime
import random

from .tool import Tool
import sqlite3


class QueryTrips(Tool):
    description = "用于查询火车票，询问用户车票类型时，请务必告诉用户有哪些车票类型。"
    description += "当用户提供完所有信息车票信息后，请立即调用该工具。"
    description += """
    下面是一个简单的对话场景：
    <用户>: 帮我看看后天的票
    <助手>: 好的，请问出发车站和到达车站是?
    <用户>: 广州到长沙
    <助手>: 请问是普通火车还是高铁，或者都可以？
    <用户>: 高铁
    <助手>: 正在为您调用接口...
    """
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

    @staticmethod
    def find_station(cursor, name: str):
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
        station_from = kwargs["station_from"].rstrip("站")
        station_to = kwargs["station_to"].rstrip("站")
        tripe_type = kwargs["trips_type"]
        print("db_path", self.db_path)
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        if date <= now_date:
            result = f"无法订购日期为{date}的车票，时间非法"
            return {"result": result}
        # -- first find station
        station_from_list = self.find_station(cursor, station_from)
        station_to_list = self.find_station(cursor, station_to)
        if len(station_from_list) == 0:
            result = f"暂时没有找到{station_from}站相关车票数据，可能是您输入错误，或者我们数据老旧（当前数据截止到2016年3月）导致的"
            print(result)
            return {"result": result}
        elif len(station_to_list) == 0:
            result = f"暂时没有找到{station_to}站相关车票数据，可能是您输入错误，或者我们数据老旧（当前数据截止到2016年3月）导致的"
            print(result)
            return {"result": result}
        temp_str = f'你的出发日期是：{date}, 出发车站为：{station_from}, 到达车站为：{station_to}, 选择的车票类型是{tripe_type}'
        print(temp_str)
        # -- second get trips -- #
        sql2 = """
        SELECT x.code, x.station_from, x.station_to,
        x."start", x."end", x."type",
        s.longitude, s.latitude, s2.longitude, s2.latitude
        FROM trips x
        left join station s
        on x.station_from = s.name
        left join station s2 
        on x.station_to = s2.name
        WHERE x.station_from in {} and x.station_to in {}
        """.format(tuple(station_from_list), tuple(station_to_list))
        if "高铁" in tripe_type:
            sql2 += ' and x."type" = 1'
        elif "普通" in tripe_type:
            sql2 += ' and x."type" = 1'
        print(sql2)
        cursor.execute(sql2)
        data_list = cursor.fetchall()
        print("执行sql完成")
        if len(data_list) == 0:
            result = f"暂时没有找到{station_from}站到{station_to}相关车票数据，可能是您输入错误，或者我们数据老旧（当前数据截止到2016年3月）导致的"
            return {"result": result}
        else:
            data_list2 = []
            for data in data_list:
                tripe_dict = {
                    "code": data[0],
                    "station_from": data[1],
                    "station_to": data[2],
                    "driving_time": data[3],
                    "arrival_time": data[4],
                }
                # 对于高铁
                # get distance
                distance = ((data[6] - data[8]) ** 2 + (data[7] - data[9]) ** 2) ** 0.5
                price_data = []
                if data[5] == 1:
                    # 二等座
                    price1 = round(distance * 50)
                    number1 = random.randint(10, 200)
                    price_dict = {
                        "type": "二等座",
                        "price": price1,
                        "number": number1
                    }
                    price_data.append(price_dict)
                    # 一等座
                    price2 = round(price1 * 1.5)
                    number2 = random.randint(10, 200)
                    price_dict = {
                        "type": "一等座",
                        "price": price2,
                        "number": number2
                    }
                    price_data.append(price_dict)
                    # 商务座
                    price3 = round(price1 * 3)
                    number3 = random.randint(50, 100)
                    price_dict = {
                        "type": "商务座",
                        "price": price3,
                        "number": number3
                    }
                    price_data.append(price_dict)
                else:
                    # 无座
                    price1 = round(distance * 20)
                    number1 = random.randint(100, 200)
                    price_dict = {
                        "type": "无座",
                        "price": price1,
                        "number": number1
                    }
                    price_data.append(price_dict)
                    # 硬座
                    price2 = price1
                    number2 = random.randint(0, 100)
                    price_dict = {
                        "type": "无座",
                        "price": price2,
                        "number": number2
                    }
                    price_data.append(price_dict)
                    # 硬卧
                    price3 = price1 * 2
                    number3 = random.randint(50, 200)
                    price_dict = {
                        "type": "硬卧",
                        "price": price3,
                        "number": number3
                    }
                    price_data.append(price_dict)
                    # 软卧
                    price4 = price1 * 4
                    number4 = random.randint(50, 200)
                    price_dict = {
                        "type": "软卧",
                        "price": price4,
                        "number": number4
                    }
                    price_data.append(price_dict)
                tripe_dict["price_data"] = price_data
                data_list2.append(tripe_dict)
            return {"result": data_list2}
