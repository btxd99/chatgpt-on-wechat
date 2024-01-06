import sqlite3

# 连接数据库（如果不存在会自动创建）
conn = sqlite3.connect('chat_database.db')
cursor = conn.cursor()

# 创建用户表
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    username TEXT,
    friend_status TEXT
)
''')

# 创建话题表
cursor.execute('''
CREATE TABLE IF NOT EXISTS topics (
    topic_id INTEGER PRIMARY KEY,
    topic_name TEXT
)
''')

# 创建聊天记录表
cursor.execute('''
CREATE TABLE IF NOT EXISTS chat_messages (
    message_id INTEGER PRIMARY KEY,
    sender_user_id INTEGER REFERENCES users(user_id),
    receiver_user_id INTEGER REFERENCES users(user_id),
    topic_id INTEGER REFERENCES topics(topic_id),
    timestamp DATETIME,
    content TEXT
)
''')

# 创建用户-话题关系表
cursor.execute('''
CREATE TABLE IF NOT EXISTS user_topics (
    user_topic_id INTEGER PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    topic_id INTEGER REFERENCES topics(topic_id)
)
''')

# 插入示例数据（假设你已经有了用户、话题等信息）
cursor.executemany('INSERT INTO users (username, friend_status) VALUES (?, ?)', [('Alice', '正常'), ('Bob', '已拉黑')])
cursor.executemany('INSERT INTO topics (topic_name) VALUES (?)', [('Python',), ('Data Science',)])
cursor.executemany('INSERT INTO user_topics (user_id, topic_id) VALUES (?, ?)', [(1, 1), (2, 2)])
cursor.executemany('INSERT INTO chat_messages (sender_user_id, receiver_user_id, topic_id, timestamp, content) VALUES (?, ?, ?, ?, ?)',
                   [(1, 2, 1, '2023-01-01 12:00:00', 'Hello Bob!'), (2, 1, 2, '2023-01-01 12:05:00', 'Hi Alice!')])

# 提交更改并关闭连接
conn.commit()
conn.close()
