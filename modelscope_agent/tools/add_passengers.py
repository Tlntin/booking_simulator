import json
import re
import os
from .tool import Tool


class AddPassengers(Tool):
    name = "add_passengers"
    description = "划重点：该工具用于新增乘客，录入姓名和身份证号码。"
    # description += "如果用户输入的身份证不合法，需要重新输入时，也调用该工具，用于录入身份证。"
    description += "严重警告：你不能凭空捏造姓名和身份证，必须从用户输入中获取信息。"
    # description += "注意：当用户信息未提供完整时，等待用户输入完成后，再调用该工具。"
    # description += "警告：已经录入的乘客不能重复录入。"
    # description += "警告：调用工具前不能发表看法，请等待调用完成后再根据返回结果回答用户问题。"
    # description += """
    # 下面是一个对话场景：
    # <客服>: 请问乘车人姓名是？
    # <用户>: xxxx
    # <客服>: 请问乘车人身份证号码是？
    # <用户>: xxxx
    # """
    parameters = [
        {
            "name": "passengers_name",
            "description": "乘车人姓名。",
            "required": True,
        },
        {
            "name": "passengers_idcard",
            "description": "乘车人身份证号。",
            "required": True,
        }
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
        passengers_path = os.path.join(uuid_dir, "passengers.json")
        # get old data
        if os.path.exists(passengers_path):
            with open(passengers_path, "rt", encoding="utf-8") as f:
                passengers_list = json.load(f)
        else:
            passengers_list = []

        passengers_name = kwargs["passengers_name"]
        passengers_idcard = kwargs.get("passengers_idcard", None)
        if passengers_idcard is None:
            result = "警告：请输入身份证信息。"
            print(result)
            return {"result": result}
        # --validate idcard -- #
        p = re.compile("^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$")
        res1 = p.match(passengers_idcard)
        if res1 is None:
            result = "警告：身份证不合法，请重新输入乘客姓名和身份证号码。"
            print(result)
            kwargs["passengers_name"] = ""
            kwargs["passengers_idcard"] = ""
            return {"result": result}
        new_data = {"name": passengers_name, "idcard": passengers_idcard}
        # new data
        if new_data in passengers_list:
            result = "警告：乘客信息已经录入过了，不能重复录入!"
            print(result)
            return {"result": result}
        passengers_list.append(new_data)
        # -- save passengers -- #
        with open(passengers_path, "wt", encoding="utf-8") as f:
            json.dump(passengers_list, f, ensure_ascii=False, indent=4)
        # return new data
        return {"result": new_data}


