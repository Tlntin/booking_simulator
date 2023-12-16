#!/usr/bin/python3
# -*- coding: utf-8 -*-
# @Time   : 2023/12/15 14:18
# @Author : Leni Lan

import os
import json
from .tool import Tool
import datetime


class RefundTickets(Tool):
    description = "划重点：该工具用于办理退票业务。"
    # description += "当用户提供完所有退票相关信息后，请立即调用该工具。"
    description += "需要先完成查询车票订单任务，才能办理退票。"
    # description += "如果用户直接办理退票，先帮他查一下所有订票信息。"
    # description += "一次只能退一张车票。若查出来出发日期只有一张票，就默认退一张，若有多张，和用户确认退票车次为哪一张"
    description += "退票成功后，请告诉用户退票车次的信息：订票人，出发日期，车次，退票金额，扣除手续费。"
    # description += """
    # 下面是一个简单的对话场景：
    # <用户>: 帮我办理一下退票业务
    # <助手>: 好的，查询到你已订购2张票，分别是2023年12月1日出发的G12次列车和2023年12月2日出发的G56次列车，
    # 请问需要办理哪趟列车的退票业务。
    # <用户>: G12次列车
    # <助手>: 正在为您调用接口...
    # """

    # description += """
    # 下面是一个简单的对话场景：
    # <用户>: 帮我办理一下G12次列车退票业务
    # <助手>: 查询到你订购了2023年12月11日出发的G12次列车，确定要办理该车次的退票业务吗？
    # <用户>: 是的
    # <助手>: 正在为您调用接口...
    # """

    # description += """
    # 下面是一个简单的对话场景：
    # <用户>: 帮我办理一下G12次列车退票业务
    # <助手>: 没有查询到你的订单，请确认你的退票信息是否准确。
    # <用户>: 好的，帮我查询一下我的订票信息
    # <助手>: 好的，查询到你有一张2023年12月15日出发的G52次列车，请问是否帮你办理退票
    # <用户>: 是的
    # <助手>: 正在为您调用接口...
    # """
    name = "refund_tickets"
    # 需要的参数
    parameters: list = [
        # {
        #     "name": "passengers_name",
        #     "description": "乘车人姓名。",
        #     "required": False,
        # },
        {
            "name": "code",
            "description": "列车车次。",
            "required": False,
        },
        {
            "name": "date",
            "description": "出发日期。",
            "required": False,
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
    def refund_rule(date, price):
        start_date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        now_date = datetime.datetime.now()
        diff_days = (now_date - start_date).days + \
                    (now_date - start_date).seconds / (3600*24)
        if diff_days >= 8:
            service_charge = 0
            refund = price
        elif 2 <= diff_days < 8:
            service_charge = round(price * 0.05, 2)
            refund = price - service_charge
        elif 1 <= diff_days < 2:
            service_charge = round(price * 0.1, 2)
            refund = price - service_charge
        else:
            service_charge = round(price * 0.2, 2)
            refund = price - service_charge

        return service_charge, refund

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

        code = kwargs.get("code", "")
        date = kwargs.get("date", "")

        order_code = [info['code'] for info in order_list]
        order_date = [info['date'] for info in order_list]

        if code and not date:
            if code in order_code:
                order_info = {}
                for index, info in enumerate(order_list):
                    if info['code'] == code:
                        order_info['code'] = code
                        order_info['date'] = info['date']
                        order_info["start"] = info["start"]
                        order_info["end"] = info["end"]
                        order_time = info["date"] + " " + info["start"] + ":00"
                        service_charge, refund = self.refund_rule(order_time, info['price'])
                        order_info['service_charge'] = service_charge
                        order_info['refund'] = refund
                        del order_list[index]
                        with open(order_path, "wt", encoding="utf-8") as f:
                            json.dump(order_list, f, indent=4, ensure_ascii=False)
                        break
                return {"result": order_info}

            else:
                result = "您输入的车次不在您的订票列表里，请检查后重新输入。"
                print(result)
                return {"result": result}

        elif code and date:
            if date in order_date:
                order_info = {}
                for index, info in enumerate(order_list):
                    if info['code'] == code and info['date'] == date:
                        order_info['code'] = code
                        order_info['date'] = info['date']
                        order_info["start"] = info["start"]
                        order_info["end"] = info["end"]
                        order_time = info["date"] + " " + info["start"] + ":00"
                        service_charge, refund = self.refund_rule(order_time, info['price'])
                        order_info['service_charge'] = service_charge
                        order_info['refund'] = refund
                        del order_list[index]
                        with open(order_path, "wt", encoding="utf-8") as f:
                            json.dump(order_list, f, indent=4, ensure_ascii=False)
                        break
                if order_info:
                    return {"result": order_info}
                else:
                    result = "您输入的车次不在您的订票列表里，请检查后重新输入。"
                    print(result)
                    return {"result": result}

        else:
            result = "当前无退票列车车次，请输入退票的列车车次。"
            print(result)
            return {"result": result}





