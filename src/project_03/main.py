import psycopg2
import io
from config import load_config
from generate_data import generate_promotions_data, generate_products_data, generate_brand_data, generate_sellers_data, generate_promotion_products_data, generate_categories_data
from utils import create_cur, truncate_table, restart_sequence

def insert_data(data,table_name, column_name=''):
    # Refresh table if needed, else comment out the 2 funcs below
    truncate_table(table_name)
    restart_sequence(table_name, column_name)

    buffer = io.StringIO()
    data.to_csv(buffer, index=False, header=False, na_rep=r'\N')
    buffer.seek(0)
    columns = tuple(data.columns)

    try:
        cur, conn = create_cur()

        cur.copy_from(buffer, table_name, sep=',', columns=columns)

        conn.commit()
        cur.close()
        conn.close()
        print(f'>>> {table_name} - Done!')
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error inserting data for {table_name}: {error}")

if __name__ == '__main__':
    insert_data(generate_brand_data(20),'brands', 'brand_id')
    insert_data(generate_categories_data(10), 'categories', 'category_id')
    insert_data(generate_sellers_data(25), 'sellers', 'seller_id')
    insert_data(generate_products_data(1000), 'products', 'product_id')
    insert_data(generate_promotions_data(10), 'promotions', 'promotion_id')
    insert_data(generate_promotion_products_data(100), 'promotion_product','promo_product_id')