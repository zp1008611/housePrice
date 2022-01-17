
import pymysql
def get_conn():
    conn = pymysql.connect(
        host='106.52.47.202',
        user='root',
        password='123456',
        db='house',
        charset='utf8'
    )
    # 创建游标
    cursor = conn.cursor(pymysql.cursors.DictCursor)
    return conn,cursor

def close_conn(conn, cursor):
    if cursor:
        cursor.close()
    if conn:
        conn.close()