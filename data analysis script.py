import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager as fm

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class EcommerceAnalyzer:
    def __init__(self, host='localhost', user='root', password='203195', database='ecommerce_analysis'):
        self.conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )

    def get_monthly_sales_trend(self):
        query = """
                SELECT DATE_FORMAT(order_date, '%Y-%m') as month, 
                       SUM(total_amount)                as sales, 
                       COUNT(DISTINCT order_id)         as orders, 
                       AVG(total_amount)                as avg_order_value
                FROM sales
                GROUP BY DATE_FORMAT(order_date, '%Y-%m')
                ORDER BY month 
                """

        df = pd.read_sql(query, self.conn)
        return df

    def get_category_performance(self):
        query = """
                SELECT p.category, 
                       COUNT(DISTINCT s.order_id) as order_count, 
                       SUM(s.total_amount)        as total_sales, 
                       AVG(s.total_amount)        as avg_sale_value, 
                       SUM(s.quantity)            as total_quantity
                FROM sales s
                         JOIN products p ON s.product_id = p.product_id
                GROUP BY p.category
                ORDER BY total_sales DESC 
                """

        df = pd.read_sql(query, self.conn)
        return df

    def get_city_performance(self):
        query = """
                SELECT city, 
                       COUNT(DISTINCT order_id)                        as order_count, 
                       SUM(total_amount)                               as total_sales, 
                       COUNT(DISTINCT customer_id)                     as customer_count, 
                       SUM(total_amount) / COUNT(DISTINCT customer_id) as sales_per_customer
                FROM sales
                GROUP BY city
                ORDER BY total_sales DESC 
                """

        df = pd.read_sql(query, self.conn)
        return df

    def get_rfm_analysis(self):
        # 获取当前日期（假设为2023年底）
        query = """
                SELECT customer_id, 
                       DATEDIFF('2023-12-31', MAX(order_date)) as recency, 
                       COUNT(DISTINCT order_id)                as frequency, 
                       SUM(total_amount)                       as monetary
                FROM sales
                GROUP BY customer_id 
                """

        rfm = pd.read_sql(query, self.conn)

        # RFM评分
        rfm['R_Score'] = pd.qcut(rfm['recency'], 5, labels=[5, 4, 3, 2, 1])
        rfm['F_Score'] = pd.qcut(rfm['frequency'], 5, labels=[1, 2, 3, 4, 5])
        rfm['M_Score'] = pd.qcut(rfm['monetary'], 5, labels=[1, 2, 3, 4, 5])

        # RFM总分
        rfm['RFM_Score'] = rfm['R_Score'].astype(str) + rfm['F_Score'].astype(str) + rfm['M_Score'].astype(str)

        # 客户分群
        def segment_customer(row):
            if row['R_Score'] >= 4 and row['F_Score'] >= 4 and row['M_Score'] >= 4:
                return '冠军客户'
            elif row['R_Score'] >= 4 and row['F_Score'] >= 3:
                return '潜力客户'
            elif row['R_Score'] >= 3 and row['F_Score'] >= 3:
                return '忠实客户'
            elif row['R_Score'] <= 2 and row['F_Score'] >= 3:
                return '流失风险客户'
            else:
                return '一般客户'

        rfm['segment'] = rfm.apply(segment_customer, axis=1)
        return rfm

    def create_visualizations(self):
        # 月度销售趋势
        monthly_sales = self.get_monthly_sales_trend()

        plt.figure(figsize=(12, 6))
        plt.plot(monthly_sales['month'], monthly_sales['sales'], marker='o', linewidth=2)
        plt.title('月度销售趋势')
        plt.xlabel('月份')
        plt.ylabel('销售额')
        plt.xticks(rotation=45)
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig('D:/wenjian/monthly_sales_trend.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 品类销售占比
        category_perf = self.get_category_performance()

        plt.figure(figsize=(10, 8))
        plt.pie(category_perf['total_sales'], labels=category_perf['category'], autopct='%1.1f%%')
        plt.title('各品类销售额占比')
        plt.savefig('D:/wenjian/category_sales_pie.png', dpi=300, bbox_inches='tight')
        plt.close()

        # 城市销售分布
        city_perf = self.get_city_performance()

        plt.figure(figsize=(12, 6))
        plt.bar(city_perf['city'], city_perf['total_sales'])
        plt.title('各城市销售额分布')
        plt.xlabel('城市')
        plt.ylabel('销售额')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('D:/wenjian/city_sales_bar.png', dpi=300, bbox_inches='tight')
        plt.close()

        # RFM客户分群
        rfm = self.get_rfm_analysis()

        plt.figure(figsize=(10, 6))
        rfm['segment'].value_counts().plot(kind='bar')
        plt.title('客户分群分布')
        plt.xlabel('客户分群')
        plt.ylabel('客户数量')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('D:/wenjian/customer_segments.png', dpi=300, bbox_inches='tight')
        plt.close()

        print("可视化图表已保存至 D:/wenjian/ 文件夹")


# 执行分析
if __name__ == "__main__":
    analyzer = EcommerceAnalyzer()
    analyzer.create_visualizations()

    # 保存分析结果到CSV
    monthly_sales = analyzer.get_monthly_sales_trend()
    category_perf = analyzer.get_category_performance()
    city_perf = analyzer.get_city_performance()
    rfm = analyzer.get_rfm_analysis()

    monthly_sales.to_csv('D:/wenjian/monthly_sales.csv', index=False, encoding='utf-8-sig')
    category_perf.to_csv('D:/wenjian/category_performance.csv', index=False, encoding='utf-8-sig')
    city_perf.to_csv('D:/wenjian/city_performance.csv', index=False, encoding='utf-8-sig')
    rfm.to_csv('D:/wenjian/rfm_analysis.csv', index=False, encoding='utf-8-sig')

    print("分析结果已保存至 D:/wenjian 文件夹")
