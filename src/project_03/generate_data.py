import random
from faker import Faker
import pandas as pd
from faker_ecommerce import EcommerceProvider

faker = Faker()
faker.add_provider(EcommerceProvider)

faker_vn = Faker('vi_VN')
faker_vn.add_provider(EcommerceProvider)

pd.set_option('display.max_columns', None)
#print(fk.company())

def generate_brand_data(num_records):
    data = {
        'brand_name': [faker.brand_name() for _ in range(num_records)],
        'country': [faker.country() for _ in range(num_records)],
        'created_at': [faker.date_time_this_decade() for _ in range(num_records)]
    }
    return pd.DataFrame(data)

def generate_categories_data(num_records):
    data = {
        'category_name': [faker.unique.random_element(elements=('Electronics', 'Fashion', 'Phones', 'Jackets', 'Head phone', 'Jeans', 'Shoes', 'AC', 'TV', 'Bags', 'Boots')) for _ in range(num_records)],
        'parent_category_id': [faker.random_int(min=1, max=num_records) for _ in range(num_records)],
        'level': [faker.random_int(min = 1, max = 2) for _ in range(num_records)],
        'created_at': [faker.date_time_this_decade() for _ in range(num_records)]
    }
    return pd.DataFrame(data)

def generate_sellers_data(num_records):
    data = {
        'seller_name': [faker_vn.unique.company() for _ in range(num_records)],
        'join_date': [faker.date_between(start_date ='-1y', end_date = 'today') for _ in range(num_records)],
        'seller_type': [faker.random_element(elements=('Official', 'Marketplace', 'B2B')) for _ in range(num_records)],
        'rating': [round(faker.random.uniform(1, 5),1) for _ in range(num_records)],
        'country': 'Vietnam'
    }
    return pd.DataFrame(data)

def generate_products_data(num_records, cate_max=10, brand_max=20, seller_max=25):
    data = {
        'product_name': [faker.product_name(include_brand=True) for _ in range(num_records)],
        'category_id': [faker.random_int(min = 1, max = cate_max) for _ in range(num_records)],
        'brand_id': [faker.random_int(min = 1, max = brand_max) for _ in range(num_records)],
        'seller_id': [faker.random_int(min=1, max=seller_max) for _ in range(num_records)],
        'price': [round(faker.random.uniform(100000, 500000),2) for _ in range(num_records)],
        'discount_price': 0.00,
        'stock_qty': [faker.random_int(min = 0, max = num_records) for _ in range(num_records)],
        'rating': [round(faker.random.uniform(1, 5),1) for _ in range(num_records)],
        'created_at': [faker.date_time_this_decade() for _ in range(num_records)],
        'is_active': [faker.boolean(chance_of_getting_true=50) for _ in range(num_records)]
    }
    return pd.DataFrame(data)

#df_brands = generate_brand_data(20)
#df_cats = generate_categories_data(10)
#df_sellers = generate_sellers_data(25)
df_products = generate_products_data(1000)
print(df_products.head(50))
print(df_products.info())