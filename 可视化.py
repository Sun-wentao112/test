import pandas as pd
import matplotlib.pyplot as plt
import json


x = input




















def visualize_job_data():
    # 设置字体以支持中文显示
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    # 读取 JSON 文件
    with open('job_data.json', 'r', encoding='utf-8') as json_file:
        data = json.load(json_file)

    # 将 JSON 数据转换为 DataFrame
    df = pd.DataFrame(data)

    # 可视化 1: 不同城市的职位数量柱状图
    plt.figure(figsize=(10, 6))
    city_job_counts = df['city'].value_counts()
    city_job_counts.plot(kind='bar', color='skyblue')
    plt.title('不同城市的职位数量')
    plt.xlabel('城市')
    plt.ylabel('职位数量')
    plt.xticks(rotation=45)  # 旋转 x 轴标签，防止重叠
    plt.show()


    # 可视化 2: 不同职位的经验要求柱状图
    plt.figure(figsize=(10, 6))
    experience_counts = df['experience'].value_counts()
    experience_counts.plot(kind='bar', color='lightgreen')
    plt.title('不同职位的经验要求')
    plt.xlabel('经验要求')
    plt.ylabel('职位数量')
    plt.xticks(rotation=45)
    plt.show()

    # 可视化 3: 不同城市的平均工资柱状图
    def convert_salary(salary):
        if isinstance(salary, str) and salary != 'N/A':
            # 去除可能的单位，如 '元/月' 或 '元/天' 以及其他特殊字符
            salary = salary.replace('元/月', '').replace('元/天', '').replace(',', '').replace(' ', '')
            try:
                return float(salary)
            except ValueError:
                return None
        return None

    df['salary'] = df['salary'].apply(convert_salary)
    df = df.dropna(subset=['salary'])  # 移除无法转换为数字的薪水数据
    average_salaries = df.groupby('city')['salary'].mean()
    plt.figure(figsize=(10, 6))
    average_salaries.plot(kind='bar', color='orange')
    plt.title('不同城市的平均工资')
    plt.xlabel('城市')
    plt.ylabel('平均工资')
    plt.xticks(rotation=45)
    plt.show()


if __name__ == "__main__":
    visualize_job_data()