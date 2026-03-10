"""
数据初始化模块
生成示例数据：5个知识点（带前置关系）、20道题、10名学生、随机作答记录
"""
import random
from database import init_db, get_db_connection, clear_db


def init_database():
    """
    初始化数据库，创建表结构并生成示例数据
    """
    # 清空数据库
    clear_db()
    # 初始化数据库表结构
    init_db()
    
    # 获取数据库连接
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 1. 创建知识点（带前置关系）
        print("创建知识点...")
        kp_names = ["基础数学", "代数", "几何", "三角函数", "微积分"]
        kp_descriptions = [
            "基础数学知识，包括加减乘除等基本运算",
            "代数知识，包括方程、不等式等",
            "几何知识，包括平面几何、立体几何等",
            "三角函数知识，包括正弦、余弦等",
            "微积分知识，包括导数、积分等"
        ]
        
        # 插入知识点
        kp_ids = []
        for name, description in zip(kp_names, kp_descriptions):
            cursor.execute(
                "INSERT INTO knowledge_points (name, description) VALUES (?, ?)",
                (name, description)
            )
            kp_ids.append(cursor.lastrowid)
        
        conn.commit()
        
        # 设置前置知识点关系
        # 代数的前置知识点是基础数学
        cursor.execute(
            "INSERT INTO knowledge_point_prerequisites (knowledge_point_id, prerequisite_id) VALUES (?, ?)",
            (kp_ids[1], kp_ids[0])
        )
        # 几何的前置知识点是基础数学
        cursor.execute(
            "INSERT INTO knowledge_point_prerequisites (knowledge_point_id, prerequisite_id) VALUES (?, ?)",
            (kp_ids[2], kp_ids[0])
        )
        # 三角函数的前置知识点是代数和几何
        cursor.execute(
            "INSERT INTO knowledge_point_prerequisites (knowledge_point_id, prerequisite_id) VALUES (?, ?)",
            (kp_ids[3], kp_ids[1])
        )
        cursor.execute(
            "INSERT INTO knowledge_point_prerequisites (knowledge_point_id, prerequisite_id) VALUES (?, ?)",
            (kp_ids[3], kp_ids[2])
        )
        # 微积分的前置知识点是代数和三角函数
        cursor.execute(
            "INSERT INTO knowledge_point_prerequisites (knowledge_point_id, prerequisite_id) VALUES (?, ?)",
            (kp_ids[4], kp_ids[1])
        )
        cursor.execute(
            "INSERT INTO knowledge_point_prerequisites (knowledge_point_id, prerequisite_id) VALUES (?, ?)",
            (kp_ids[4], kp_ids[3])
        )
        
        conn.commit()
        
        # 2. 创建题目
        print("创建题目...")
        question_ids = []
        for i in range(20):
            # 生成题目内容
            content = f"题目{i+1}: 这是一道关于{kp_names[i%5]}的题目"
            # 生成难度等级（1-5）
            difficulty = (i % 5) + 1
            cursor.execute(
                "INSERT INTO questions (content, difficulty) VALUES (?, ?)",
                (content, difficulty)
            )
            question_ids.append(cursor.lastrowid)
        
        conn.commit()
        
        # 3. 创建Q矩阵（题目-知识点关联）
        print("创建Q矩阵...")
        for i, question_id in enumerate(question_ids):
            # 为每个题目关联1-2个知识点
            kp_indices = random.sample(range(5), random.randint(1, 2))
            for kp_idx in kp_indices:
                cursor.execute(
                    "INSERT INTO q_matrix (question_id, knowledge_point_id, weight) VALUES (?, ?, ?)",
                    (question_id, kp_ids[kp_idx], 1)
                )
        
        conn.commit()
        
        # 4. 创建学生
        print("创建学生...")
        student_ids = []
        for i in range(10):
            name = f"学生{i+1}"
            student_id = f"S{i+1:03d}"
            cursor.execute(
                "INSERT INTO students (name, student_id) VALUES (?, ?)",
                (name, student_id)
            )
            student_ids.append(cursor.lastrowid)
        
        conn.commit()
        
        # 5. 创建X矩阵（学生-作答记录）
        print("创建X矩阵...")
        for student_id in student_ids:
            # 每个学生随机作答15-20道题
            answered_questions = random.sample(question_ids, random.randint(15, 20))
            for question_id in answered_questions:
                # 随机生成作答结果（1表示正确，0表示错误）
                score = 1 if random.choice([True, False]) else 0
                cursor.execute(
                    "INSERT INTO x_matrix (student_id, question_id, score) VALUES (?, ?, ?)",
                    (student_id, question_id, score)
                )
        
        conn.commit()
        
        print("数据初始化完成！")
        
    except Exception as e:
        print(f"数据初始化失败: {e}")
        conn.rollback()
    finally:
        conn.close()


if __name__ == "__main__":
    init_database()
