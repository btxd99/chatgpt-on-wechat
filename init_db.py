import sqlite3
from datetime import datetime
import json

from common.log import logger


def initialize_database(database_name):
    # 连接到数据库
    if not database_name:
        database_name = 'default_database_name.db'
    logger.info("[Database] initialize_database {}".format(database_name))
    conn = sqlite3.connect(database_name)
    cursor = conn.cursor()

    # 用户信息表
    user_info_table = """
    CREATE TABLE IF NOT EXISTS user_info (
        user_id TEXT PRIMARY KEY,
        nickname TEXT,
        relationship_status TEXT,
        friend_added_time TEXT,
        friend_removed_time TEXT,
        relationship_intimacy TEXT
    );
    """

    # 聊天记录表
    chat_record_table = """
    CREATE TABLE IF NOT EXISTS chat_record (
        msg_id TEXT PRIMARY KEY NOT NULL,
        create_time TEXT NOT NULL,
        ctype TEXT,
        content TEXT,
        from_user_id TEXT,
        from_user_nickname TEXT,
        to_user_id TEXT,
        to_user_nickname TEXT,
        other_user_id TEXT,
        other_user_nickname TEXT,
        is_group TEXT,
        is_at TEXT,
        actual_user_id TEXT,
        actual_user_nickname TEXT,
        self_display_name TEXT
    );
    """

    # 话题记录表
    topic_record_table = """
    CREATE TABLE IF NOT EXISTS topic_record (
        topic_id TEXT PRIMARY KEY,
        topic_name TEXT NOT NULL,
        topic_type TEXT,
        creation_time TEXT,
        topic_status TEXT
    );
    """

    # 执行创建表的 SQL 语句
    cursor.executescript(user_info_table)
    cursor.executescript(chat_record_table)
    cursor.executescript(topic_record_table)

    # 提交并关闭连接
    conn.commit()
    conn.close()

