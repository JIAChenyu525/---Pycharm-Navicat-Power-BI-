import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import matplotlib.pyplot as plt

# 设置中文显示
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

# 定义类EcommerceDataGenerator
class EcommerceDataGenerator:
    def __init__(self, start_date="2024-01-01", end_date="2024-12-31"):
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d") # 起始时间
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d") # 终止时间
        self.dates = pd.date_range(start_date, end_date) # 时间范围

    def generate_products(self, num_products=100):
        categories = {
            '电子产品': ['智能手机', '笔记本电脑', '平板电脑', '智能手表', '耳机'],
            '服装': ['T恤', '牛仔裤', '连衣裙', '外套', '运动鞋'],
            '家居': ['沙发', '床', '餐桌', '椅子', '柜子'],
            '美妆': ['口红', '粉底液', '眼影', '面膜', '香水'],
            '食品': ['零食', '饮料', '生鲜', '粮油', '调味品']
        }

        products = []
        product_id = 1

        for category, subcategories in categories.items():
            for subcategory in subcategories:
                for i in range(num_products // len(categories) // len(subcategories)):
                    cost_price = round(np.random.uniform(
                        50 if category == "食品" else 100,
                        500 if category == "食品" else 2000
                    ), 2)

                    products.append({
                        'product_id': product_id,
                        'product_name': f"{subcategory}{i}",
                        'category': category,
                        'subcategory': subcategory,
                        'cost_price': cost_price,
                        'selling_price': round(cost_price * np.random.uniform(1.2, 2.5), 2),
                        'supplier': f"供应商{random.randint(1, 20)}"
                    })
                    product_id += 1

        return pd.DataFrame(products)

    def generate_customers(self, num_customers=1000):
        cities = ['深圳', '广州', '北京', '上海', '杭州', '成都', '武汉', '南京']
        age_groups = ['18-25', '26-35', '36-45', '46-55', '55+']

        customers = []

        for i in range(num_customers):
            join_date = self.start_date + timedelta(days=random.randint(0, 100))
            customers.append({
                'customer_id': 1000 + i,
                'name': f"客户{1000 + i}",
                'city': random.choice(cities),
                'age_group': random.choice(age_groups),
                'join_date': join_date.strftime("%Y-%m-%d")
            })

        return pd.DataFrame(customers)

    def generate_sales(self, products_df, customers_df, num_transactions=10000):
        sales = []
        order_id = 10000

        # 创建日期销售权重（周末和节假日销量更高）
        date_weights = {}
        for date in self.dates:
            weight = 1.0
            if date.weekday() >= 5:  # 周末
                weight = 1.5
            if date.month in [1, 2, 10, 12]:  # 节假日月份
                weight *= 1.2
            date_weights[date] = weight

        # 生成销售记录
        for _ in range(num_transactions):
            order_date = random.choices(self.dates, weights=[date_weights[d] for d in self.dates])[0]
            customer = customers_df.iloc[random.randint(0, len(customers_df) - 1)]
            product = products_df.iloc[random.randint(0, len(products_df) - 1)]

            quantity = np.random.poisson(1.5) + 1  # 确保至少购买1件

            sales.append({
                'order_id': order_id,
                'order_date': order_date.strftime("%Y-%m-%d"),
                'customer_id': customer['customer_id'],
                'product_id': product['product_id'],
                'quantity': quantity,
                'unit_price': product['selling_price'],
                'city': customer['city']
            })
            order_id += 1

        sales_df = pd.DataFrame(sales)
        sales_df['total_amount'] = sales_df['unit_price'] * sales_df['quantity']

        return sales_df

    # 生成数据，三个
    def generate_all_data(self):
        print("生成产品数据...")
        products_df = self.generate_products()

        print("生成客户数据...")
        customers_df = self.generate_customers()

        print("生成销售数据...")
        sales_df = self.generate_sales(products_df, customers_df)

        # 保存数据(products.csv, customers.csv, sales.csv)
        products_df.to_csv('D:/wenjian/products.csv', index=False, encoding='utf-8-sig')
        customers_df.to_csv('D:/wenjian/customers.csv', index=False, encoding='utf-8-sig')
        sales_df.to_csv('D:/wenjian/sales.csv', index=False, encoding='utf-8-sig')

        print("数据生成完成!")
        return products_df, customers_df, sales_df


# 执行数据生成
if __name__ == "__main__":
    generator = EcommerceDataGenerator()
    products, customers, sales = generator.generate_all_data()