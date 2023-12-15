import json
import re
import os
from .tool import Tool


class ShowPassengers(Tool):
    name = "show_passengers"
    description = "划重点：该工具用于显示已有乘客信息"
    description += "调用完成后，告诉用户已经录入了几个乘客，乘客姓名和身份证号。"
    # description += "如果用户没有录入任何乘客信息，可以询问用户是否调用<add_passengers>工具添加新乘客。"
    # description += "警告：调用工具前不能发表看法，请等待调用完成后再根据返回结果回答用户问题。"
    parameters = []

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
            new_data_list = []
            for data in passengers_list:
                data["idcard"] = data["idcard"][:-12] + "." * 8 + data["idcard"][-4:]
                new_data_list.append(data)
            return {"result": new_data_list}
        else:
            result = "警告：您还没有录入过任何乘客信息，需要添加吗？"
            print(result)
            return {"result": result}
