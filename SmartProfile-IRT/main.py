"""
主程序入口模块
用于测试数据库连接和数据完整性
"""
from database import get_db_connection


def test_database():
    """
    测试数据库连接和数据完整性
    """
    # 获取数据库连接
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 测试知识点数据
        print("\n=== 测试知识点数据 ===")
        cursor.execute("SELECT * FROM knowledge_points")
        kps = cursor.fetchall()
        print(f"知识点数量: {len(kps)}")
        for kp in kps:
            # 获取前置知识点
            cursor.execute(
                "SELECT kp.name FROM knowledge_points kp JOIN knowledge_point_prerequisites kpp ON kp.id = kpp.prerequisite_id WHERE kpp.knowledge_point_id = ?",
                (kp['id'],)
            )
            prereq_names = [row['name'] for row in cursor.fetchall()]
            print(f"知识点: {kp['name']}, 前置知识点: {prereq_names}")
        
        # 测试题目数据
        print("\n=== 测试题目数据 ===")
        cursor.execute("SELECT * FROM questions")
        questions = cursor.fetchall()
        print(f"题目数量: {len(questions)}")
        for q in questions[:5]:  # 只显示前5道题
            print(f"题目: {q['content']}, 难度: {q['difficulty']}")
        
        # 测试Q矩阵数据
        print("\n=== 测试Q矩阵数据 ===")
        cursor.execute("SELECT * FROM q_matrix")
        q_matrices = cursor.fetchall()
        print(f"Q矩阵记录数量: {len(q_matrices)}")
        for qm in q_matrices[:5]:  # 只显示前5条记录
            print(f"题目ID: {qm['question_id']}, 知识点ID: {qm['knowledge_point_id']}, 权重: {qm['weight']}")
        
        # 测试学生数据
        print("\n=== 测试学生数据 ===")
        cursor.execute("SELECT * FROM students")
        students = cursor.fetchall()
        print(f"学生数量: {len(students)}")
        for s in students:
            print(f"学生: {s['name']}, 学生ID: {s['student_id']}")
        
        # 测试X矩阵数据
        print("\n=== 测试X矩阵数据 ===")
        cursor.execute("SELECT * FROM x_matrix")
        x_matrices = cursor.fetchall()
        print(f"X矩阵记录数量: {len(x_matrices)}")
        for xm in x_matrices[:5]:  # 只显示前5条记录
            print(f"学生ID: {xm['student_id']}, 题目ID: {xm['question_id']}, 得分: {xm['score']}")
        
        print("\n数据库测试完成！")
        
    except Exception as e:
        print(f"数据库测试失败: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    # 首先运行数据初始化
    import init_data
    init_data.init_database()
    
    # 然后测试数据库
    test_database()
    
    # 测试 DINA 模型
    print("\n=== 测试 DINA 模型 ===")
    from irt_model import test_dina_model
    test_dina_model()
