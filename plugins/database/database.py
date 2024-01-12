# encoding:utf-8

import json
import os
import re
import sqlite3
from datetime import datetime

import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import ReplyType
from common.log import logger
from init_db import initialize_database


@plugins.register(
    name="Database",
    desire_priority=950,
    hidden=True,
    desc="将聊天消息保存到数据库中。",
    version="1.0",
    author="btxd99",
)
class Database(Plugin):
    def __init__(self):
        super().__init__()
        try:
            # load config
            conf = super().load_config()
            curdir = os.path.dirname(__file__)
            if not conf:
                # 配置不存在则写入默认配置
                config_path = os.path.join(curdir, "config.json")
                if not os.path.exists(config_path):
                    conf = {"database_name": "your_database_name.db"}
                    with open(config_path, "w") as f:
                        json.dump(conf, f, indent=4)

            self.database_name = conf.get("database_name", 'default_database_name.db')
            initialize_database(self.database_name)
            self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
            self.handlers[Event.ON_DECORATE_REPLY] = self.on_decorate_reply
            logger.debug("[Database] inited")
        except Exception as e:
            logger.warn("[Database] init failed, ignore or see plugins/database.")
            raise e

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return
        try:
            e_context.action = EventAction.CONTINUE

            # 获取消息对象内容
            cmsg = e_context["context"]["msg"]
            logger.debug("[Database] on_handle_context. cmsg: %s" % cmsg)

            # 构造插入消息记录的SQL
            insert_sql = """
            INSERT INTO chat_record (
                msg_id, create_time, ctype, content, from_user_id, from_user_nickname,
                to_user_id, to_user_nickname, other_user_id, other_user_nickname,
                is_group, is_at, actual_user_id, actual_user_nickname, self_display_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            conn = sqlite3.connect(self.database_name)
            cursor = conn.cursor()

            # 执行插入操作
            cursor.execute(insert_sql, (
                str(cmsg.msg_id), str(cmsg.create_time), str(cmsg.ctype), str(e_context["context"].content),
                str(cmsg.from_user_id), str(cmsg.from_user_nickname), str(cmsg.to_user_id), str(cmsg.to_user_nickname),
                str(cmsg.other_user_id), str(cmsg.other_user_nickname), str(cmsg.is_group), str(cmsg.is_at),
                str(cmsg.actual_user_id), str(cmsg.actual_user_nickname), str(cmsg.self_display_name)
            ))

            # 提交并关闭连接
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warn("[Database] on_handle_context failed, ignore or see plugins/database.")
            raise e

    def on_decorate_reply(self, e_context: EventContext):
        # 如果不是文本类型，则忽略
        if e_context["reply"].type not in [ReplyType.TEXT, ReplyType.ERROR, ReplyType.INFO]:
            return
        try:
            e_context.action = EventAction.CONTINUE

            # 获取消息对象内容
            cmsg = e_context["context"]["msg"]
            logger.debug("[Database] on_decorate_reply. reply: %s" % e_context["reply"])

            # 构造插入消息记录的SQL
            insert_sql = """
            INSERT INTO chat_record (
                msg_id, create_time, ctype, content, from_user_id, from_user_nickname,
                to_user_id, to_user_nickname, other_user_id, other_user_nickname,
                is_group, is_at, actual_user_id, actual_user_nickname, self_display_name
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """

            # 获取当前时间戳
            timestamp = int(datetime.now().timestamp())

            conn = sqlite3.connect(self.database_name)
            cursor = conn.cursor()

            # 执行插入操作
            cursor.execute(insert_sql, (
                str(int(cmsg.msg_id) + 1), str(timestamp), str(cmsg.ctype), str(e_context["reply"].content),
                str(cmsg.to_user_id), str(cmsg.to_user_nickname), str(cmsg.from_user_id), str(cmsg.from_user_nickname),
                str(cmsg.other_user_id), str(cmsg.other_user_nickname), str(cmsg.is_group), str(cmsg.is_at),
                str(cmsg.actual_user_id), str(cmsg.actual_user_nickname), str(cmsg.self_display_name)
            ))

            # 提交并关闭连接
            conn.commit()
            conn.close()
        except Exception as e:
            logger.warn("[Database] on_decorate_reply failed, ignore or see plugins/database.")
            raise e

    def get_help_text(self, **kwargs):
        return "将聊天消息保存到数据库中"
