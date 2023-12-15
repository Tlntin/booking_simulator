import json
import re
import os
from .tool import Tool


class AddPassengers(Tool):
    name = "add_passengers"
    description = "用于新增乘客"
    description += "如果用户输入的身份证不合法，需要重新输入时，也调用该工具，用于录入身份证。"
    description += "严重警告：你不能凭空捏造姓名和身份证，必须从用户输入中获取信息。"
    description += "已经录入的乘客不能重复录入"
    parameters = [
        {
            "name": "passengers_name",
            "description": "乘车人姓名。如果未提供姓名，则要求用户输入姓名。",
            "required": True,
        },
        {
            "name": "passengers_idcard",
            "description": "乘车人身份证号，如果填写则必须是13位数字，最后一位可以为字母X",
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
        passengers_idcard = kwargs["passengers_idcard"]
        # --validate idcard -- #
        p = re.compile("^[1-9]\d{5}(18|19|20)\d{2}((0[1-9])|(1[0-2]))(([0-2][1-9])|10|20|30|31)\d{3}[0-9Xx]$")
        res1 = p.match(passengers_idcard)
        if res1 is None:
            result = "身份证不合法，请重新输入。"
            print(result)
            return {"result": result}
        new_data = {"name": passengers_name, "idcard": passengers_idcard}
        # new data
        if new_data in passengers_list:
            result = "乘客信息已经录入过了，不能重复录入"
            print(result)
            return {"result": result}
        passengers_list.append(new_data)
        # -- save passengers -- #
        with open(passengers_path, "wt", encoding="utf-8") as f:
            json.dump(passengers_list, f)
        # return new data
        return {"result": new_data}


