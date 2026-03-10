"""
SmartProfile 项目的 Streamlit 可视化 Demo
展示学生的知识点掌握概率和个性化学习建议
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from database import get_db_connection
from irt_model import DinaModel


# 初始化 DINA 模型
model = DinaModel()
model.train()


# 获取知识点名称映射
def get_knowledge_point_names():
    """
    从数据库获取知识点ID到名称的映射
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM knowledge_points")
    kp_names = {row[0]: row[1] for row in cursor.fetchall()}
    conn.close()
    return kp_names


# 获取学生列表
def get_students():
    """
    从数据库获取学生列表
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, student_id FROM students")
    students = [(row[0], f"{row[1]} ({row[2]})") for row in cursor.fetchall()]
    conn.close()
    return students


# 生成个性化学习建议
def generate_learning_advice(student_id, mastery_prob, kp_names):
    """
    生成个性化学习建议
    
    Args:
        student_id: 学生ID
        mastery_prob: 掌握概率字典
        kp_names: 知识点名称映射
        
    Returns:
        学习建议列表
    """
    advice = []
    weak_knowledge_points = []
    
    # 找出掌握概率 < 0.5 的知识点
    for kp_id, prob in mastery_prob.items():
        if prob < 0.5:
            weak_knowledge_points.append((kp_id, prob))
    
    # 按掌握概率排序（从低到高）
    weak_knowledge_points.sort(key=lambda x: x[1])
    
    # 生成学习建议
    if weak_knowledge_points:
        advice.append(f"您好！根据您的作答情况，我们发现您在以下知识点上需要加强：")
        
        for kp_id, prob in weak_knowledge_points:
            kp_name = kp_names.get(kp_id, f"知识点{kp_id}")
            advice.append(f"- **{kp_name}**（掌握概率：{prob:.2f}）")
        
        advice.append("\n建议学习计划：")
        
        # 基于前置关系的学习顺序建议
        conn = get_db_connection()
        cursor = conn.cursor()
        
        for kp_id, _ in weak_knowledge_points:
            # 获取前置知识点
            cursor.execute(
                "SELECT kp.name FROM knowledge_points kp JOIN knowledge_point_prerequisites kpp ON kp.id = kpp.prerequisite_id WHERE kpp.knowledge_point_id = ?",
                (kp_id,)
            )
            prerequisites = [row[0] for row in cursor.fetchall()]
            
            kp_name = kp_names.get(kp_id, f"知识点{kp_id}")
            if prerequisites:
                advice.append(f"- 学习 **{kp_name}** 前，建议先复习：{', '.join(prerequisites)}")
            else:
                advice.append(f"- 学习 **{kp_name}**，这是一个基础知识点")
        
        conn.close()
        
        advice.append("\n学习方法建议：")
        advice.append("1. 针对薄弱知识点，多做相关练习题")
        advice.append("2. 建立知识点之间的联系，形成知识网络")
        advice.append("3. 定期复习，巩固已学知识")
        advice.append("4. 遇到困难时，及时寻求帮助")
    else:
        advice.append("恭喜您！您对所有知识点的掌握情况都很好。")
        advice.append("建议您继续保持，并尝试挑战更高级的知识点。")
    
    return advice


# 主应用
st.title("SmartProfile - 学生知识掌握分析")

# 获取数据
students = get_students()
kp_names = get_knowledge_point_names()

# 学生选择
st.sidebar.header("学生选择")
student_options = {name: id for id, name in students}
selected_student_name = st.sidebar.selectbox(
    "请选择学生",
    list(student_options.keys())
)
selected_student_id = student_options[selected_student_name]

# 获取学生掌握概率
mastery_prob = model.get_student_mastery(selected_student_id)

# 展示学生信息
st.header(f"{selected_student_name} 的知识掌握情况")

# 雷达图展示
st.subheader("知识点掌握概率 - 雷达图")
if mastery_prob:
    # 准备数据
    kp_ids = list(mastery_prob.keys())
    kp_names_list = [kp_names.get(kp_id, f"知识点{kp_id}") for kp_id in kp_ids]
    probabilities = list(mastery_prob.values())
    
    # 创建雷达图
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=probabilities,
        theta=kp_names_list,
        fill='toself',
        name='掌握概率'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 1]
            )
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig)
else:
    st.warning("未找到该学生的掌握概率数据")

# 表格展示
st.subheader("知识点掌握概率 - 表格")
if mastery_prob:
    # 准备表格数据
    table_data = []
    for kp_id, prob in mastery_prob.items():
        table_data.append({
            "知识点": kp_names.get(kp_id, f"知识点{kp_id}"),
            "掌握概率": f"{prob:.2f}"
        })
    
    # 创建 DataFrame
    df = pd.DataFrame(table_data)
    
    # 按掌握概率排序
    df = df.sort_values(by="掌握概率", ascending=False)
    
    # 展示表格
    st.dataframe(df, width='stretch')
else:
    st.warning("未找到该学生的掌握概率数据")

# 个性化学习建议
st.subheader("个性化学习建议")
if mastery_prob:
    advice = generate_learning_advice(selected_student_id, mastery_prob, kp_names)
    for line in advice:
        st.write(line)
else:
    st.warning("无法生成学习建议")

# 页脚
st.markdown("---")
st.markdown("© 2026 SmartProfile 项目")
