import psycopg2
import io
from src.project_03.config import load_config

def create_cur():
    config = load_config()
    conn = psycopg2.connect(**config)
    cur = conn.cursor()
    return cur,conn

def fetch_sequence_name(table_name, column_name):
    # pg_get_serial_sequence returns the sequence name in 'schema.sequence' format
    command = "SELECT pg_get_serial_sequence(%s, %s);"

    try:
        cur, conn = create_cur()
        cur.execute(command, (table_name, column_name))

        result = cur.fetchone()

        cur.close()
        conn.close()

        # If a sequence exists, it returns a string; otherwise, it returns None
        if result and result[0]:
            return result[0]
        return False

    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error fetching sequence for {table_name}: {error}")
        return False

def truncate_table(table_name):
    try:
        sql = f"TRUNCATE {table_name} CASCADE;"
        cur, conn = create_cur()
        cur.execute(sql)
        conn.commit()
        cur.close()
        conn.close()
        print(f'Truncated {table_name}.')
    except (psycopg2.DatabaseError, Exception) as error:
        print(error)

def resync_sequence(table_name, column_name):
    sequence = fetch_sequence_name(table_name,column_name)
    command = f"ALTER SEQUENCE {sequence} RESTART;"
    try:
        cur, conn = create_cur()
        cur.execute(command)
        conn.commit()
        cur.close()
        conn.close()
        print(f'resynced sequence for {table_name}.')
    except (psycopg2.DatabaseError, Exception) as error:
        print(f"Error resync sequence for {table_name}: {error}")
        return False

#truncate_table('promotion_product')
#print(fetch_sequence_name('promotion_product', 'promo_product_id'))