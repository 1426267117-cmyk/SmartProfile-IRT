"""
数据库连接和配置模块
使用 Python 内置的 sqlite3 模块，无需额外安装服务
"""
import sqlite3
import os

# 数据库文件路径
DB_PATH = 'smartprofile.db'

def get_db_connection():
    """
    获取数据库连接
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # 使查询结果可以通过列名访问
    return conn

def init_db():
    """
    初始化数据库，创建表结构
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 创建知识点表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_points (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE,
        description TEXT
    )
    ''')
    
    # 创建知识点前置关系中间表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS knowledge_point_prerequisites (
        knowledge_point_id INTEGER,
        prerequisite_id INTEGER,
        PRIMARY KEY (knowledge_point_id, prerequisite_id),
        FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points (id),
        FOREIGN KEY (prerequisite_id) REFERENCES knowledge_points (id)
    )
    ''')
    
    # 创建题目表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        content TEXT NOT NULL,
        difficulty INTEGER NOT NULL
    )
    ''')
    
    # 创建Q矩阵表（题目-知识点关联）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS q_matrix (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        knowledge_point_id INTEGER NOT NULL,
        weight INTEGER NOT NULL DEFAULT 1,
        FOREIGN KEY (question_id) REFERENCES questions (id),
        FOREIGN KEY (knowledge_point_id) REFERENCES knowledge_points (id)
    )
    ''')
    
    # 创建学生表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        student_id TEXT NOT NULL UNIQUE
    )
    ''')
    
    # 创建X矩阵表（学生-作答记录）
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS x_matrix (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER NOT NULL,
        question_id INTEGER NOT NULL,
        score INTEGER NOT NULL,  -- 0表示错误，1表示正确
        FOREIGN KEY (student_id) REFERENCES students (id),
        FOREIGN KEY (question_id) REFERENCES questions (id)
    )
    ''')
    
    conn.commit()
    conn.close()


def clear_db():
    """
    清空数据库，删除所有表
    """
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
