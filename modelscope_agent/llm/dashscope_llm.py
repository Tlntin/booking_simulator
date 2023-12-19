import os
import random
import traceback
from http import HTTPStatus
from typing import Union

import dashscope
import time
from collections import OrderedDict
import json
from dashscope import Generation
from modelscope_agent.agent_types import AgentType

from .base import LLM
from .utils import DEFAULT_MESSAGE, CustomOutputWrapper

dashscope.api_key = os.getenv('DASHSCOPE_API_KEY')


class DashScopeLLM(LLM):
    name = 'dashscope_llm'

    def __init__(self, cfg):
        super().__init__(cfg)
        self.model = self.cfg.get('model', 'modelscope-agent-llm-v1')
        self.model_id = self.model
        self.generate_cfg = self.cfg.get('generate_cfg', {})
        self.agent_type = self.cfg.get('agent_type', AgentType.DEFAULT)

    def generate(self,
                 llm_artifacts: Union[str, dict],
                 functions=[],
                 **kwargs):
        print("call generate")
        failed_time = 0
        failed_code_freq = OrderedDict()
        failed_message_freq = OrderedDict()
        for i in range(3):
            print("call generate at {} time".format(i + 1))
            try:
                if self.agent_type == AgentType.Messages:
                    messages = llm_artifacts if len(
                        llm_artifacts) > 0 else DEFAULT_MESSAGE
                    self.generate_cfg['use_raw_prompt'] = False
                    response = dashscope.Generation.call(
                        model=self.model,
                        messages=messages,
                        # set the random seed, optional, default to 1234 if not set
                        seed=random.randint(1, 10000),
                        result_format=
                        'message',  # set the result to be "message" format.
                        stream=False,
                        **self.generate_cfg)
                    if response.status_code == HTTPStatus.OK:
                        llm_result = CustomOutputWrapper.handle_message_chat_completion(
                            response)
                        return llm_result
                    else:
                        err_msg = 'Error Request id: %s, Code: %d, status: %s, message: %s' % (
                            response.request_id, response.status_code, response.code,
                            response.message)
                        print(err_msg)
                        failed_code_freq[response.status_code] = failed_code_freq.get(response.status_code, 0) + 1
                        failed_message_freq[response.message] = failed_message_freq.get(response.message, 0) + 1
                        failed_time += 1
                        time.sleep(i * 2 + 1)
                else:
                    response = Generation.call(
                        model=self.model,
                        prompt=llm_artifacts,
                        stream=False,
                        **self.generate_cfg)
                    if response.status_code == HTTPStatus.OK:
                        llm_result = CustomOutputWrapper.handle_message_text_completion(
                            response)
                        return llm_result
                    else:
                        err_msg = 'Error Request id: %s, Code: %d, status: %s, message: %s' % (
                            response.request_id, response.status_code, response.code,
                            response.message)
                        print(err_msg)
                        failed_code_freq[response.status_code] = failed_code_freq.get(response.status_code, 0) + 1
                        failed_message_freq[response.message] = failed_message_freq.get(response.message, 0) + 1
                        failed_time += 1
                        time.sleep(i * 2 + 1)
            except Exception as e:
                error = traceback.format_exc()
                error_msg = f'LLM error with input {llm_artifacts} \n dashscope error: {str(e)} with traceback {error}'
                print(error_msg)
                # raise RuntimeError(error)
                time.sleep(i * 2 + 1)
        if failed_time == 3:
            last_failed_code = list(failed_code_freq.keys())[-1]
            last_failed_message = list(failed_message_freq.keys())[-1]
            return '调用模型失败，错误码：{}，错误信息：{}'.format(last_failed_code, last_failed_message)

        if self.agent_type == AgentType.MS_AGENT:
            # in the form of text
            idx = llm_result.find('<|endofthink|>')
            if idx != -1:
                llm_result = llm_result[:idx + len('<|endofthink|>')]
            return llm_result
        elif self.agent_type == AgentType.Messages:
            # in the form of message
            return llm_result
        else:
            # in the form of text
            return llm_result

    def stream_generate(self,
                        llm_artifacts: Union[str, dict],
                        functions=[],
                        **kwargs):
        print("call stream generate")
        failed_time = 0
        failed_code_freq = OrderedDict()
        failed_message_freq = OrderedDict()
        for i in range(3):
            print("call stream generate at {} time".format(i + 1))
            total_response = ''
            try:
                if self.agent_type == AgentType.Messages:
                    self.generate_cfg['use_raw_prompt'] = False
                    responses = Generation.call(
                        model=self.model,
                        messages=llm_artifacts,
                        stream=True,
                        result_format='message',
                        **self.generate_cfg)
                else:
                    responses = Generation.call(
                        model=self.model,
                        prompt=llm_artifacts,
                        stream=True,
                        **self.generate_cfg)
            except Exception as e:
                error = traceback.format_exc()
                error_msg = f'LLM error with input {llm_artifacts} \n dashscope error: {str(e)} with traceback {error}'
                print(error_msg)
                # raise RuntimeError(error)
                failed_time += 1
                time.sleep(i * 2 + 1)
                continue

            for response in responses:
                if response.status_code == HTTPStatus.OK:
                    if self.agent_type == AgentType.Messages:
                        llm_result = CustomOutputWrapper.handle_message_chat_completion(
                            response)
                        frame_text = llm_result['content'][len(total_response):]
                    else:
                        llm_result = CustomOutputWrapper.handle_message_text_completion(
                            response)
                        frame_text = llm_result[len(total_response):]
                    yield frame_text

                    if self.agent_type == AgentType.Messages:
                        total_response = llm_result['content']
                    else:
                        total_response = llm_result
                else:
                    err_msg = 'Error Request id: %s, Code: %d, status: %s, message: %s' % (
                        response.request_id, response.status_code, response.code,
                        response.message)
                    print(err_msg)
                    failed_code_freq[response.status_code] = failed_code_freq.get(response.status_code, 0) + 1
                    failed_message_freq[response.message] = failed_message_freq.get(response.message, 0) + 1
                    failed_time += 1
                    time.sleep(i * 2 + 1)
                    # raise RuntimeError(err_msg)
            if failed_time == 0:
                break
        if failed_time == 3:
            last_failed_code = list(failed_code_freq.keys())[-1]
            last_failed_message = list(failed_message_freq.keys())[-1]
            yield '调用模型失败，错误码：{}，错误信息：{}'.format(last_failed_code, last_failed_message)