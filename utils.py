import time
import pymysql
def get_time():
    time_str = time.strftime("%Y{}%m{}%d{} %X")
    return time_str.format("年", "月", "日")
def get_model1_name():
    with open('model1Name.txt','r',encoding='gbk') as file:
        data=file.read()
    lis = data.split(',')
    name = lis[:-1]
    dic=dict()
    dic[0]=len(name)
    for i in range(len(name)):
        dic[i+1]=lis[i]
    return dic
# 数据库   
def get_conn():
    conn = pymysql.connect(
        host='106.52.47.202',
        user='root',
        password='123456',
        db='house',
        charset='utf8'
    )
    # 创建游标
    cursor = conn.cursor()
    return conn,cursor

def close_conn(conn,cursor):
    cursor.close()
    conn.close()

def query(sql,*args):
    """
    封装通用查询
    :param sql:
    :param args:
    :return: 返回查询到的结果，以((),())的形式
    """
    conn, cursor = get_conn()
    cursor.execute(sql,args)
    res = cursor.fetchall()
    close_conn(conn, cursor)
    return res
def get_data():
    sql = "select area,price,avePrice from sevenDay"
    res = query(sql)
    # 获取全部数据
    return res
if __name__ == '__main__':
    pass
    # print(get_time())
    # print(get_data())