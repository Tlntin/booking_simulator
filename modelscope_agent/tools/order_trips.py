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
    下面是一个简单的对话场景：
    <用户>：帮我订一张明天的，广州到北京的票
    <客服>: 好的，即将查询剩余车票。
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
            "description": "车票类型：对于高铁，可选二等座/一等座/商务座；对于普通火车，可选无座/硬座/硬卧/软卧",
            "required": True,
        },
        {
            "name": "seat_type",
            "description": "座位：有5个位置，分别为左侧的<A>/<B>/<C>位, 以及右侧的<E>/<F>位; 其中<A>和<F>为靠窗座位，<C>和<E>为靠过道座位。当你询问用户做哪个位置的时候，记得告诉用户这些位置的特点。",
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
    def find_trips(cursor, code: str):
        """
        :param cursor:
        :param code: trips code
        :return:
        """
        sql = f"""
        SELECT x.code, x.station_from, x.station_to, x."start", x."end", x."type",
        x.second_class_price, x.first_class_price, x.business_class_price,
        x.no_seat_price, x.hard_seat_price, x.hard_sleeper_price, x.soft_sleeper_price
        FROM trips x
        WHERE x.code = "{code}"
        """
        cursor.execute(sql)
        data = cursor.fetchone()
        if len(data) > 0:
            dict1 = {
                "code": data[0],
                "station_from": data[1],
                "station_to": data[2],
                "start": data[3],
                "end": data[4],
                "type": data[5],
            }
            price_dict = {}
            if data[5] == 1:
                price_dict["second_class"] = data[6]
                price_dict["first_class"] = data[7]
                price_dict["business_class"] = data[8]
            else:
                price_dict["no_seat"] = data[9]
                price_dict["hard_seat"] = data[10]
                price_dict["hard_sleeper"] = data[11]
                price_dict["soft_sleeper"] = data[12]
            dict1["price_data"] = price_dict
        else:
            dict1 = {}
        return dict1

    def _local_call(self, *args, **kwargs):
        date = kwargs['date']
        now_date = datetime.datetime.now().strftime("%Y-%m-%d")
        train_code = kwargs["train_code"]
        trips_type = kwargs["trips_type"]
        seat_type = kwargs.get("seat_type", None)
        passengers_name = kwargs["passengers_name"]
        passengers_idcard = kwargs.get("passengers_idcard", None)
        if seat_type is None or seat_type == "":
            result = "请您选择合适的座位：有5个位置，分别为左侧的`A`/`B`/`C`位, 以及右侧的`E`/`F`位; 其中`A`和`F`为靠窗座位，`C`和`E`为靠过道座位。"
            print(result)
            return {"result": result}
        print("db_path", self.db_path)
        db = sqlite3.connect(self.db_path)
        cursor = db.cursor()
        if date <= now_date:
            result = f"无法订购日期为{date}的车票，时间非法"
            cursor.close()
            db.close()
            return {"result": result}
        try:
            query_date = datetime.datetime.strptime(date, "%Y-%m-%d")
            now_date = datetime.datetime.now()
            if query_date.day - now_date.day > 14:
                result = f"当前只能预定14天内的车票，请您重新选择日期。"
                print(result)
                cursor.close()
                db.close()
                return {"result": result}
        except:
            result = f"您输入的日期格式不对，您可以输入像2023-12-03这样格式的日期哈"
            print(result)
            cursor.close()
            db.close()
            return {"result": result}
        # --- find trips -- #
        print("call find trips")
        trips_data = self.find_trips(cursor, train_code)
        print("call find trips OK")
        if trips_data["type"] == 1:
            suggestion_seat = "二等座/一等座/商务座"
        else:
            suggestion_seat = "无座/硬座/硬卧/软卧"

        result = "您输入的车次{}没有{}，我们仅提供{}, 请检查后重新输入。"
        if len(trips_data) == 0:
            result = f"您输入的车次{train_code}没有找到, 请检查后重新输入。"
            print(result)
            cursor.close()
            db.close()
            return {"result": result}
        price_dict = trips_data["price_data"]
        if "二等" in trips_type:
            price = price_dict.get("second_class")
            trips_type = "二等座"
            if price is None:
                result = result.format(train_code, trips_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "一等" in trips_type:
            price = price_dict.get("first_class")
            trips_type = "一等座"
            if price is None:
                result = result.format(train_code, trips_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "商务" in trips_type:
            price = price_dict.get("business_class")
            trips_type = "商务座"
            if price is None:
                result = result.format(train_code, trips_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "无座" in trips_type:
            price = price_dict.get("no_seat")
            trips_type = "无座"
            if price is None:
                cursor.close()
                db.close()
                result = result.format(train_code, trips_type, suggestion_seat)
                return {"result": result}
        elif "硬座" in trips_type:
            price = price_dict.get("hard_seat")
            trips_type = "硬座"
            if price is None:
                result = result.format(train_code, trips_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "硬卧" in trips_type:
            price = price_dict.get("hard_sleeper")
            trips_type = "硬卧"
            if price is None:
                result = result.format(train_code, trips_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "软卧" in trips_type:
            price = price_dict.get("soft_sleeper")
            trips_type = "软卧"
            if price is None:
                result = result.format(train_code, trips_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        else:
            result = result.format(train_code, trips_type, suggestion_seat)
            cursor.close()
            db.close()
            return {"result": result}
        # find passengers #
        # todo
        # valid id card

        result_dict = {
            "code": trips_data["code"],
            "station_from": trips_data["station_from"],
            "station_to": trips_data["station_to"],
            "start": trips_data["start"],
            "end": trips_data["end"],
            "type": "高铁" if trips_data["type"] else "普通火车",
            "trips_type": trips_type,
            "price": price,
            "carriage_number": random.randint(1, 18),
            "seat_number": random.randint(1, 24),
            "seat_type": seat_type,
            "passengers_name": passengers_name,
            # "passengers_idcard": passengers_idcard[:6] + "*" * 6 + passengers_idcard[-4: ]
        }
        # -- save order -- #
        # todo
        return {"result": result_dict}






