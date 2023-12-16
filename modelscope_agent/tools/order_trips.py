import datetime
import json
import random
import os
import re
import sqlite3

from .tool import Tool


class OrderTrips(Tool):
    description = "划重点：该工具用于订购车票。"
    # description += "当用户提供完所有订票相关信息后，请立即调用该工具。"
    description += "需要先完成车票查询任务，才能订购车票。"
    # description += "如果用户直接订购车票，先帮他查一下车票"
    description += """
    补充信息：
    座位类型：对于高铁，可选二等座/一等座/商务座；对于普通火车，可选无座/硬座/硬卧/软卧。
    座位位置：有5个位置，分别为左侧的`A`/`B`/`C`位, 以及右侧的`E`/`F`位; 其中`A`和`F`为靠窗座位，`C`和`E`为靠过道座位。
    """
    # description += "请你耐心检查用户输入，对于用户未输入的信息，请用对老年人的尊敬的语气询问用户其缺失的信息。"
    # description += "注意：当用户信息未提供完整时，等待用户输入完成后，再调用该工具。"
    description += "订票成功后，请告诉用户车次，出发站，到达站，开车时间，到达时间，座位类型，车厢号，座位号。"
    description += "订票成功后，用query_weather工具查询并告诉用户当天始发站和终到站的天气情况。"
    # description += """
    # 下面是一个简单的对话场景：
    # <用户>: 帮我订购明天的，G32车次的，二等座
    # <客服>：好的，请问乘车人是？
    #
    # 下面是一个简单的对话场景：
    # <用户>：帮我订一张明天的，广州到北京的票
    # <客服>: 好的，即将查询剩余车票。
    # """
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
            "name": "seat_type",
            "description": "座位类型",
            "required": True,
        },
        # {
        #     "name": "passengers_name",
        #     "description": "乘车人姓名。",
        #     "required": True,
        # },
        # {
        #     "name": "passengers_idcard",
        #     "description": "乘车人身份证号。",
        #     "required": False,
        # },
        {
            "name": "seat_position",
            "description": "座位位置。",
            "required": True,
        },
        # {
        #     "name": "trips_numer",
        #     "description": "订票数量。",
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
        uuid_str = kwargs["uuid_str"]
        print("uuid str", uuid_str)
        default_agent_dir = '/tmp/agentfabric'
        default_builder_config_dir = os.path.join(default_agent_dir, 'config')
        model_cfg_file = os.getenv('BUILDER_CONFIG_DIR', default_builder_config_dir)
        uuid_dir = os.path.join(model_cfg_file, uuid_str)
        print("uuid_dir", uuid_dir)
        order_path = os.path.join(uuid_dir, "order.json")
        # -- load old order -- #
        if os.path.exists(order_path):
            with open(order_path, "rt") as f:
                order_list = json.load(f)
        else:
            order_list = []
        date = kwargs['date']
        now_date = datetime.datetime.now().strftime("%Y-%m-%d")
        train_code = kwargs["train_code"]
        seat_type = kwargs["seat_type"]
        seat_position = kwargs.get("seat_position", "")
        # passengers_name = kwargs.get("passengers_name", "")
        # passengers_idcard = kwargs.get("passengers_idcard", "")
        # trips_numer = kwargs.get("trips_numer", 1)
        # if passengers_name is None or passengers_name == "":
        #     result = "警告：请您提供乘车人姓名。"
        #     print(result)
        #     return {"result": result}
        # # valid passengers_idcard
        # if len(passengers_idcard) > 0:
        #     p = re.compile(
        #         "^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$")
        #     res1 = p.match(passengers_idcard)
        #     if res1 is None:
        #         result = f"警告：乘客{passengers_name}的身份证信息有误，需要先添加乘客信息，才能继续购票。"
        #         print(result)
        #         return {"result": result}
        # new_data = {"name": passengers_name, "idcard": passengers_idcard}
        # load passengers informations
        # print("get passengers infomation")
        # passengers_path = os.path.join(uuid_dir, "passengers.json")
        # if os.path.exists(passengers_path):
        #     with open(passengers_path, "rt", encoding="utf-8") as f:
        #         passengers_list = json.load(f)
        #         print("passengers_list", passengers_list)
        #         # if user not provide idcard
        #         if len(passengers_idcard) == 0:
        #             passengers_list = [
        #                 temp for temp in passengers_list
        #                 if temp["name"] == passengers_name
        #             ]
        #             print("passengers_list", passengers_list)
        #             if len(passengers_list) == 0:
        #                 result = f"警告：您还没有录入过乘客{passengers_name}的信息，需要先添加乘客信息，才能继续购票。"
        #                 print(result)
        #                 return {"result": result}
        #             else:
        #                 passengers_dict = passengers_list[0]
        #                 idcard = passengers_dict["idcard"]
        #         else:
        #             idcard = passengers_idcard
        # elif len(passengers_idcard) == 0:
        #     result = "警告：您还没有录入过任何乘客信息，需要先添加乘客，才能继续购票。"
        #     print(result)
        #     return {"result": result}
        # else:
        #     idcard = passengers_idcard
        # if trips_numer != 1:
        #     result = "当前每次仅支持订一张票"
        #     print(result)
        #     return {"result": result}
        if "A" in seat_position:
            seat_position = "A"
        elif "B" in seat_position:
            seat_position = "B"
        elif "C" in seat_position:
            seat_position = "C"
        elif "E" in seat_position:
            seat_position = "E"
        elif "F" in seat_position:
            seat_position = "F"
        else:
            print(seat_position)
            result = "请您选择合适的座位：有5个位置，分别为左侧的`A`/`B`/`C`位, 以及右侧的`E`/`F`位; 其中`A`和`F`为靠窗座位，`C`和`E`为靠过道座位。"
            print(result)
            return {"result": result}
        
        print("get passengers infomation ok!")
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
        # validate order has conflict
        for temp in order_list:
            if temp["date"] == date:
                if temp["start"] <= trips_data["start"] <= temp["end"]:
                    result = "当天已经存在一个即将出行的行程，该订单与其存在时间冲突或重复。"
                    print(result)
                    cursor.close()
                    db.close()
                    return result
        price_dict = trips_data["price_data"]
        if "二等" in seat_type:
            price = price_dict.get("second_class")
            seat_type = "二等座"
            if price is None:
                result = result.format(train_code, seat_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "一等" in seat_type:
            price = price_dict.get("first_class")
            seat_type = "一等座"
            if price is None:
                result = result.format(train_code, seat_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "商务" in seat_type:
            price = price_dict.get("business_class")
            seat_type = "商务座"
            if price is None:
                result = result.format(train_code, seat_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "无座" in seat_type:
            price = price_dict.get("no_seat")
            seat_type = "无座"
            if price is None:
                cursor.close()
                db.close()
                result = result.format(train_code, seat_type, suggestion_seat)
                return {"result": result}
        elif "硬座" in seat_type:
            price = price_dict.get("hard_seat")
            seat_type = "硬座"
            if price is None:
                result = result.format(train_code, seat_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "硬卧" in seat_type:
            price = price_dict.get("hard_sleeper")
            seat_type = "硬卧"
            if price is None:
                result = result.format(train_code, seat_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        elif "软卧" in seat_type:
            price = price_dict.get("soft_sleeper")
            seat_type = "软卧"
            if price is None:
                result = result.format(train_code, seat_type, suggestion_seat)
                cursor.close()
                db.close()
                return {"result": result}
        else:
            result = result.format(train_code, seat_type, suggestion_seat)
            cursor.close()
            db.close()
            return {"result": result}
        # find passengers #
        # todo
        # valid id card

        result_dict = {
            "code": trips_data["code"],
            "date": date,
            "station_from": trips_data["station_from"],
            "station_to": trips_data["station_to"],
            "start": trips_data["start"],
            "end": trips_data["end"],
            "type": "高铁" if trips_data["type"] else "普通火车",
            "trips_type": seat_type,
            "price": price,
            "carriage_number": random.randint(1, 18),
            "seat_number": str(random.randint(1, 24)) + seat_position,
            # "passengers_name": passengers_name,
            # "passengers_idcard": idcard,
        }
        # -- save order -- #
        order_list.append(result_dict)
        with open(order_path, "wt") as f:
            json.dump(order_list, f, ensure_ascii=False, indent=4)
        return {"result": result_dict}






