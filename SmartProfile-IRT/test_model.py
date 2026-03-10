"""
测试 DINA 模型和数据处理
不依赖 Streamlit 的可视化界面
"""
from irt_model import DinaModel
from database import get_db_connection


def test_dina_model():
    """
    测试 DINA 模型
    """
    print("初始化 DINA 模型...")
    model = DinaModel()
    
    print("训练模型...")
    model.train()
    
    # 获取知识点名称映射
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM knowledge_points")
    kp_names = {row[0]: row[1] for row in cursor.fetchall()}
    
    # 获取学生列表
    cursor.execute("SELECT id, name, student_id FROM students")
    students = [(row[0], f"{row[1]} ({row[2]})") for row in cursor.fetchall()]
    conn.close()
    
    print("\n测试学生掌握概率...")
    # 测试所有学生
    for student_id, student_name in students:
        mastery = model.get_student_mastery(student_id)
        print(f"\n学生 {student_name} 的掌握概率:")
        for kp_id, prob in mastery.items():
            kp_name = kp_names.get(kp_id, f"知识点{kp_id}")
            print(f"  - {kp_name}: {prob:.2f}")
    
    print("\n测试完成！")


if __name__ == "__main__":
    test_dina_model()
