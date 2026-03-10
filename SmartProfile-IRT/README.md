# SmartProfile-IRT 环境配置与运行指南

## 环境依赖
- Python 版本：3.8 及以上
- 核心依赖包：
  - sqlalchemy：数据库操作
  - pandas/numpy：数据处理与算法计算
  - streamlit：轻量化可视化界面
  - matplotlib：雷达图绘制
- 安装命令：
  pip install sqlalchemy pandas numpy streamlit matplotlib
- 环境验证：
  python -c "import sqlalchemy, pandas, numpy, streamlit; print('环境配置成功')"

## 运行流程
1. 初始化数据库：
   执行 `python database.py`，生成 `smartprofile.db` 数据库文件，完成Q/X矩阵与知识图谱数据初始化。
2. 验证算法逻辑：
   执行 `python irt_model.py`，终端输出学生知识点掌握概率，验证IRT算法计算正确性。
3. 启动可视化Demo：
   执行 `streamlit run app.py`，自动打开浏览器界面（http://localhost:8501），选择学生ID查看认知雷达图与学习建议。

