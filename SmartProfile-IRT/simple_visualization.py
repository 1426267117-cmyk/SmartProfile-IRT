"""
简化版可视化脚本
使用 matplotlib 生成知识点掌握概率的雷达图和表格
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from irt_model import DinaModel
from database import get_db_connection


def generate_visualization():
    """
    生成知识点掌握概率的可视化
    """
    print("初始化 DINA 模型...")
    model = DinaModel()
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
    
    # 为每个学生生成可视化
    for student_id, student_name in students[:3]:  # 只生成前3个学生的可视化
        print(f"\n生成 {student_name} 的可视化...")
        
        # 获取掌握概率
        mastery = model.get_student_mastery(student_id)
        
        # 准备数据
        kp_ids = list(mastery.keys())
        kp_names_list = [kp_names.get(kp_id, f"知识点{kp_id}") for kp_id in kp_ids]
        probabilities = list(mastery.values())
        
        # 生成雷达图
        generate_radar_chart(student_name, kp_names_list, probabilities)
        
        # 生成表格
        generate_table(student_name, kp_names_list, probabilities)
    
    print("\n可视化生成完成！")


def generate_radar_chart(student_name, kp_names, probabilities):
    """
    生成雷达图
    """
    # 计算角度
    N = len(kp_names)
    angles = np.linspace(0, 2 * np.pi, N, endpoint=False).tolist()
    angles += angles[:1]  # 闭合
    
    # 复制最后一个值以闭合图表
    values = probabilities + probabilities[:1]
    
    # 创建图表
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    ax.plot(angles, values, linewidth=2, linestyle='solid', label=student_name)
    ax.fill(angles, values, alpha=0.25)
    
    # 设置标签
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(kp_names)
    
    # 设置范围
    ax.set_ylim(0, 1)
    
    # 添加标题
    plt.title(f"{student_name} 的知识点掌握概率", size=15, y=1.1)
    
    # 保存图表
    plt.savefig(f"{student_name}_radar.png")
    plt.close()
    print(f"  雷达图已保存为: {student_name}_radar.png")


def generate_table(student_name, kp_names, probabilities):
    """
    生成表格
    """
    # 创建数据框
    data = {
        "知识点": kp_names,
        "掌握概率": [f"{p:.2f}" for p in probabilities]
    }
    df = pd.DataFrame(data)
    
    # 按掌握概率排序
    df['掌握概率数值'] = probabilities
    df = df.sort_values(by="掌握概率数值", ascending=False)
    df = df.drop("掌握概率数值", axis=1)
    
    # 保存为CSV文件
    df.to_csv(f"{student_name}_table.csv", index=False, encoding='utf-8-sig')
    print(f"  表格已保存为: {student_name}_table.csv")


if __name__ == "__main__":
    generate_visualization()
