import psycopg2
from config import load_config
def create_tables():
    """ Create tables in the PostgreSQL database"""
    commands = ("""
        CREATE TABLE IF NOT EXISTS brands(
            brand_id SERIAL PRIMARY KEY,
            brand_name VARCHAR(100) NOT NULL,
            country VARCHAR(50) NOT NULL,
            created_at TIMESTAMP NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS categories(
            category_id SERIAL PRIMARY KEY,
            category_name VARCHAR(100) NOT NULL,
            parent_category_id INTEGER NULL REFERENCES categories(category_id),
            level SMALLINT NOT NULL CHECK (status_code IN (1, 2)),
            created_at TIMESTAMP NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS sellers(
            seller_id SERIAL PRIMARY KEY,
            seller_name VARCHAR(150) NOT NULL,
            join_date DATE NOT NULL,
            seller_type VARCHAR(50) NOT NULL,
            rating DECIMAL(2,1),
            country VARCHAR(50) NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS products(
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(200) NOT NULL,
            category_id INTEGER NOT NULL REFERENCES categories(category_id),
            brand_id INTEGER NOT NULL REFERENCES brands(brand_id),
            seller_id INTEGER NOT NULL REFERENCES sellers(seller_id),
            price DECIMAL(12,2) NOT NULL,
            discount_price DECIMAL(12,2),
            stock_qty INTEGER,
            rating FLOAT,
            created_at TIMESTAMP NOT NULL,
            is_active BOOLEAN NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS orders(
            order_id SERIAL PRIMARY KEY,
            order_date TIMESTAMP NOT NULL,
            seller_id INT NOT NULL REFERENCES sellers(seller_id),
            status VARCHAR(20),
            total_amount DECIMAL(12,2),
            created_at TIMESTAMP NOT NULL
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS order_items(
            order_item_id SERIAL PRIMARY KEY,
            order_id INT NOT NULL REFERENCES orders(order_id),
            product_id INT NOT NULL REFERENCES products(product_id),
            quantity INT,
            unit_price DECIMAL(12,2),
            subtotal DECIMAL(12,2)
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS promotions(
            promotion_id SERIAL PRIMARY KEY,
            promotion_name VARCHAR(100) NOT NULL,
            promotion_type VARCHAR(50) NOT NULL,
            discount_type VARCHAR(20),
            discount_value NUMERIC(10,2),
            start_date DATE NOT NULL,
            end_date DATE
        )
        """,
        """
        CREATE TABLE IF NOT EXISTS promotion_product(
            promo_product_id SERIAL PRIMARY KEY,
            promotion_id INT NOT NULL REFERENCES promotions(promotion_id),
            product_id INT NOT NULL REFERENCES products(product_id),
            created_at TIMESTAMP NOT NULL
        )
        """
    )

    try:
        config = load_config()
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # execute the CREATE TABLE statement
                #for command in commands:
                cur.execute(commands)

    except (psycopg2.DatabaseError, Exception) as error:
        print(error)
if __name__ == '__main__':
    create_tables()