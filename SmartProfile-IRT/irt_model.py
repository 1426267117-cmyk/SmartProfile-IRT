"""
IRT 模型实现模块
实现简化版 DINA 模型，计算学生在知识点上的掌握概率
"""
import numpy as np
from database import get_db_connection


class DinaModel:
    """
    简化版 DINA 模型类
    用于计算学生在知识点上的掌握概率
    """
    
    def __init__(self):
        """
        初始化 DINA 模型
        """
        # 加载数据
        self.q_matrix = None  # Q矩阵：题目-知识点关联
        self.x_matrix = None  # X矩阵：学生-作答记录
        self.student_ids = []  # 学生ID列表
        self.knowledge_point_ids = []  # 知识点ID列表
        self.question_ids = []  # 题目ID列表
        self.load_data()
        
        # 模型参数
        self.g = 0.2  # 猜测参数：未掌握知识点时答对的概率
        self.s = 0.1  # 失误参数：掌握知识点时答错的概率
        
        # 学生掌握状态概率
        self.mastery_prob = None  # 每个学生在每个知识点上的掌握概率
    
    def load_data(self):
        """
        从数据库加载 Q 矩阵和 X 矩阵
        """
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 加载知识点ID
            cursor.execute("SELECT id FROM knowledge_points ORDER BY id")
            self.knowledge_point_ids = [row[0] for row in cursor.fetchall()]
            
            # 加载题目ID
            cursor.execute("SELECT id FROM questions ORDER BY id")
            self.question_ids = [row[0] for row in cursor.fetchall()]
            
            # 加载学生ID
            cursor.execute("SELECT id FROM students ORDER BY id")
            self.student_ids = [row[0] for row in cursor.fetchall()]
            
            # 构建Q矩阵：题目×知识点
            num_questions = len(self.question_ids)
            num_knowledge_points = len(self.knowledge_point_ids)
            self.q_matrix = np.zeros((num_questions, num_knowledge_points), dtype=int)
            
            # 填充Q矩阵
            cursor.execute("SELECT question_id, knowledge_point_id FROM q_matrix")
            for row in cursor.fetchall():
                question_id, kp_id = row
                q_idx = self.question_ids.index(question_id)
                kp_idx = self.knowledge_point_ids.index(kp_id)
                self.q_matrix[q_idx, kp_idx] = 1
            
            # 构建X矩阵：学生×题目
            num_students = len(self.student_ids)
            self.x_matrix = np.zeros((num_students, num_questions), dtype=int)
            
            # 填充X矩阵
            cursor.execute("SELECT student_id, question_id, score FROM x_matrix")
            for row in cursor.fetchall():
                student_id, question_id, score = row
                s_idx = self.student_ids.index(student_id)
                q_idx = self.question_ids.index(question_id)
                self.x_matrix[s_idx, q_idx] = score
            
        except Exception as e:
            print(f"加载数据失败: {e}")
        finally:
            conn.close()
    
    def calculate_posterior(self, student_idx):
        """
        计算学生的后验概率
        
        Args:
            student_idx: 学生索引
            
        Returns:
            后验概率数组
        """
        num_knowledge_points = len(self.knowledge_point_ids)
        num_states = 2 ** num_knowledge_points  # 所有可能的掌握状态组合
        
        # 初始化先验概率（均匀分布）
        prior = np.ones(num_states) / num_states
        
        # 计算似然度
        likelihood = np.ones(num_states)
        
        # 遍历每个题目
        for q_idx in range(len(self.question_ids)):
            # 获取学生的作答结果
            response = self.x_matrix[student_idx, q_idx]
            
            # 如果学生没有作答该题，跳过
            if response == -1:
                continue
            
            # 遍历每个可能的掌握状态
            for state_idx in range(num_states):
                # 将状态索引转换为二进制表示（掌握状态）
                mastery_state = np.array([int(bit) for bit in bin(state_idx)[2:].zfill(num_knowledge_points)])
                
                # 检查是否掌握了该题所需的所有知识点
                required_knowledge = self.q_matrix[q_idx]
                has_all_knowledge = np.all(mastery_state & required_knowledge == required_knowledge)
                
                # 计算答对的概率
                if has_all_knowledge:
                    # 掌握了所有知识点，答错的概率为 s
                    p_correct = 1 - self.s
                else:
                    # 未掌握所有知识点，答对的概率为 g
                    p_correct = self.g
                
                # 更新似然度
                if response == 1:
                    likelihood[state_idx] *= p_correct
                else:
                    likelihood[state_idx] *= (1 - p_correct)
        
        # 计算后验概率
        posterior = prior * likelihood
        posterior /= np.sum(posterior)  # 归一化
        
        return posterior
    
    def calculate_mastery_prob(self, posterior):
        """
        根据后验概率计算每个知识点的掌握概率
        
        Args:
            posterior: 后验概率数组
            
        Returns:
            每个知识点的掌握概率数组
        """
        num_knowledge_points = len(self.knowledge_point_ids)
        num_states = 2 ** num_knowledge_points
        
        mastery_prob = np.zeros(num_knowledge_points)
        
        # 遍历每个知识点
        for kp_idx in range(num_knowledge_points):
            # 遍历每个可能的掌握状态
            for state_idx in range(num_states):
                # 将状态索引转换为二进制表示
                mastery_state = np.array([int(bit) for bit in bin(state_idx)[2:].zfill(num_knowledge_points)])
                
                # 检查该状态是否掌握了当前知识点
                if mastery_state[kp_idx] == 1:
                    mastery_prob[kp_idx] += posterior[state_idx]
        
        return mastery_prob
    
    def train(self, max_iterations=100, tolerance=1e-6):
        """
        使用EM算法训练模型
        
        Args:
            max_iterations: 最大迭代次数
            tolerance: 收敛阈值
        """
        num_students = len(self.student_ids)
        num_knowledge_points = len(self.knowledge_point_ids)
        
        # 初始化掌握概率
        self.mastery_prob = np.zeros((num_students, num_knowledge_points))
        
        # 迭代训练
        for iteration in range(max_iterations):
            # E步：计算后验概率和掌握概率
            new_mastery_prob = np.zeros((num_students, num_knowledge_points))
            
            for s_idx in range(num_students):
                # 计算后验概率
                posterior = self.calculate_posterior(s_idx)
                # 计算掌握概率
                new_mastery_prob[s_idx] = self.calculate_mastery_prob(posterior)
            
            # 检查收敛
            if np.max(np.abs(new_mastery_prob - self.mastery_prob)) < tolerance:
                print(f"模型在第 {iteration+1} 次迭代收敛")
                break
            
            # 更新掌握概率
            self.mastery_prob = new_mastery_prob
        
        # 如果没有收敛
        if iteration == max_iterations - 1:
            print(f"模型在 {max_iterations} 次迭代后未收敛")
    
    def get_student_mastery(self, student_id):
        """
        获取指定学生的知识点掌握概率
        
        Args:
            student_id: 学生ID
            
        Returns:
            掌握概率字典，键为知识点ID，值为掌握概率
        """
        # 检查学生ID是否存在
        if student_id not in self.student_ids:
            return {}
        
        # 获取学生索引
        s_idx = self.student_ids.index(student_id)
        
        # 构建掌握概率字典
        mastery_dict = {}
        for kp_idx, kp_id in enumerate(self.knowledge_point_ids):
            mastery_dict[kp_id] = float(self.mastery_prob[s_idx, kp_idx])
        
        return mastery_dict


# 测试函数
def test_dina_model():
    """
    测试 DINA 模型
    """
    print("初始化 DINA 模型...")
    model = DinaModel()
    
    print("训练模型...")
    model.train()
    
    print("测试学生掌握概率...")
    # 测试前3个学生
    for student_id in model.student_ids[:3]:
        mastery = model.get_student_mastery(student_id)
        print(f"学生 {student_id} 的掌握概率: {mastery}")


if __name__ == "__main__":
    test_dina_model()
