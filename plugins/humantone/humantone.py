# encoding:utf-8

import json
import os
import re
import time

import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *


@plugins.register(
    name="Humantone",
    desire_priority=80,
    hidden=True,
    desc="把回复内容改成人类答复习惯：删除部分标点符号、删除机器人常用的各种礼貌/正式术语、拆分成多句。",
    version="1.0",
    author="btxd99",
)
class Humantone(Plugin):
    def __init__(self):
        super().__init__()
        self.content_ignore_list = None
        try:
            # load config
            conf = super().load_config()
            curdir = os.path.dirname(__file__)
            if not conf:
                # 配置不存在则写入默认配置
                config_path = os.path.join(curdir, "config.json")
                if not os.path.exists(config_path):
                    conf = {"content_min_length": 1, "max_statement": 0, "content_ignore_list": [""],
                            "reply_filter_list": [""]}
                    with open(config_path, "w") as f:
                        json.dump(conf, f, indent=4)

            self.content_ignore_list = conf.get("content_ignore_list", [])
            self.reply_filter_list = conf.get("reply_filter_list", [])
            self.content_min_length = conf.get("content_min_length", 0)
            self.max_statement = conf.get("max_statement", 0)
            self.punctuation_to_filter = conf.get("punctuation_to_filter", "")
            self.max_punctuation = conf.get("max_punctuation", 0)
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            self.handlers[Event.ON_DECORATE_REPLY] = self.on_decorate_reply
            logger.info("[HumanTone] inited")
        except Exception as e:
            logger.warn(
                "[HumanTone] init failed, ignore or see plugins/humanTone .")
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type not in [ContextType.TEXT]:
            return

        # 获取上下文内容
        content = e_context["context"].content
        logger.info("[HumanTone] on_handle_context. content: %s" % content)
        # 如果消息内容小于最小长度，则忽略，用于过滤一些无意义的消息
        if len(content) < self.content_min_length:
            logger.info(f"[HumanTone] Ignore: Len < {self.content_min_length} , ignore this msg.")
            e_context.action = EventAction.BREAK_PASS
            return
        # 遍历忽略列表，如果上下文内容匹配到忽略列表中的内容，则忽略
        for re_content_ignore in self.content_ignore_list:
            re_content_ignore = re.compile(re_content_ignore, flags=0)
            logger.debug(f"[HumanTone] Ignore: Try match {re_content_ignore} .")
            if re_content_ignore.match(content):
                logger.info(f"[HumanTone] Ignore: Match {re_content_ignore} in {content}, ignore this msg.")
                e_context.action = EventAction.BREAK_PASS
                return

    def on_decorate_reply(self, e_context: EventContext):
        if e_context["reply"].type not in [ReplyType.TEXT]:
            return

        reply = e_context["reply"]
        reply_text = reply.content
        logger.debug("[HumanTone] on_decorate_reply. content: %s" % reply_text)

        # 遍历过滤器列表，对回复文本进行过滤
        for re_reply_filter in self.reply_filter_list:
            re_reply_filter = re.compile(re_reply_filter, flags=0)
            logger.debug(f"[HumanTone] Filter: Try match {re_reply_filter} in {reply_text}.")
            logger.debug(f"[HumanTone] Filter: Match {re_reply_filter} in {reply_text}, filter it.")
            reply_text = re_reply_filter.sub("", reply_text)

        # 如果过滤后的文本中包含最大标点符号数，则换成"\n \n \n"拆分文本
        if len(re.findall(self.punctuation_to_filter, reply_text)) > self.max_punctuation:
            reply_text = re.sub(self.punctuation_to_filter, "\n \n \n", reply_text)
        reply_text = reply_text.strip()
        logger.debug(f"[HumanTone] Reply: reply_text: {reply_text}")
        reply = Reply(ReplyType.TEXT, reply_text)
        e_context["reply"] = reply
        e_context.action = EventAction.CONTINUE

        # 模拟打字速度
        # logger.debug("Typing {} words, sleep {} s".format(len(reply_text), 1 + 0.7 * len(reply_text)))
        # time.sleep(1 + 0.7 * len(reply_text))

        # else:
        #     reply_list = [reply_text]
        # # 如果max_statement存在且大于0，则丢弃后面的内容，以免说太多
        # if self.max_statement > 0:
        #     if len(reply_list) > self.max_statement:
        #         reply_list = reply_list[:self.max_statement]
        #         logger.debug(f"[HumanTone] Truncated: len(reply_list) > {self.max_statement}, truncated the end")

        # for each_line in reply_list:
        #     reply.content = each_line.strip()
        #     # 模拟打字速度
        #     time.sleep(1 + 0.7 * len(each_line))
        #     logger.debug("Typing {} words, sleep {} s".format(len(each_line), 1 + 0.7 * len(each_line)))
        #     self.send(reply, context)

    def get_help_text(self, **kwargs):
        return "把回复内容改成人类答复习惯：删除部分标点符号、删除机器人常用的各种礼貌/正式术语、拆分成多句"
