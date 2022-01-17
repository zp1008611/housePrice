# encoding: utf-8
import pymysql
from getURL import getDayUrl,getUrl
from getJingtaiData import get_jingtai_data
from getCommunityData import get_community_data
from getIpPool import makeIp
import time
import traceback
import random
import datetime
import sys
from conn import get_conn,close_conn

def update_count():
    try:
        cursor = None
        conn = None
        conn, cursor = get_conn()
        stopTime = random.uniform(0,1)
        time.sleep(stopTime)
        DayUrl_dic = getDayUrl()
        # {房子ID:{'发布时间':releaseTime, '所在区域':area, '总价':price}}
        try:
            time_sql = "SELECT DISTINCT releaseTime FROM sevenDay ORDER BY releaseTime ASC LIMIT 1"
            cursor.execute(time_sql)
            data=cursor.fetchall()
            if int((datetime.datetime.now()-data[0].get('releaseTime')).days) > 7:
                del_sql="DELETE FROM sevenDay WHERE releaseTime=%s"
                cursor.execute(del_sql,data[0].get('releaseTime'))
                conn.commit()
        except:
            pass
        logFile = open('crawlerlog.txt', 'a')
        logFile.write(f"================{time.asctime()}=================")
        logFile.write("\n")
        logFile.write(f'{time.asctime()}数量数据开始更新')
        logFile.write("\n")
        logFile.close()
        conn, cursor = get_conn()
        insert_sql = "insert into sevenDay values(%s, %s, %s, %s, %s, %s)"
        sql_query = "select houseID from sevenDay where releaseTime=%(releaseTime)s and houseID=%(id)s"
        for key,value in DayUrl_dic.items():
            if not cursor.execute(sql_query, {'releaseTime':value.get('releaseTime'),'id':key}):
                cursor.execute(insert_sql, [key, value.get('releaseTime'), value.get('area'), value.get('price'), value.get('avePrice'), value.get('houseurl')])
        conn.commit()  # 提交事务 update delete insert操作
        logFile = open('crawlerlog.txt', 'a')
        logFile.write(f"================{time.asctime()}=================\n")
        logFile.write(f'{time.asctime()}数量数据更新完毕')
        logFile.write("\n")
        logFile.close()
    except:
        # traceback.print_exc()
        errorFile = open('errorlog.txt', 'a')
        errorFile.write(f"================{time.asctime()}=================")
        errorFile.write(traceback.format_exc())
        errorFile.close()
    finally:
        close_conn(conn, cursor)
        
def update_seven():
    try:
        cursor = None
        conn = None
        conn, cursor = get_conn()
        time_sql = "SELECT DISTINCT releaseTime FROM sevenDay ORDER BY releaseTime ASC LIMIT 1"
        cursor.execute(time_sql)
        data=cursor.fetchall()
        if int((datetime.datetime.now()-data[0].get('releaseTime')).days) == 7:
            seven_sql="SELECT * FROM sevenDay WHERE releaseTime=%s"
            cursor.execute(seven_sql,data[0].get('releaseTime'))
            url_lis=cursor.fetchall()
            logFile = open('crawlerlog.txt', 'a')
            logFile.write(f"================{time.asctime()}=================\n")
            logFile.write(f'{time.asctime()}七天前数据开始更新')
            logFile.write("\n")
            logFile.close()
            houseFieldName=[]
            houseField_sql = "SELECT COLUMN_NAME FROM information_schema.`COLUMNS` WHERE TABLE_NAME = 'eachhouse'"
            cursor.execute(houseField_sql)
            houseField_data=cursor.fetchall()
            houseInsert = "insert into eachhouse values("
            for i in range(len(houseField_data)):
                houseFieldName.append(houseField_data[i].get('COLUMN_NAME'))
                if i!=len(houseField_data)-1:
                    houseInsert += '%s,'
                else:
                    houseInsert += '%s'
            houseInsert += ')'
            communityFieldName=[]
            communityField_sql = "SELECT COLUMN_NAME FROM information_schema.`COLUMNS` WHERE TABLE_NAME = 'community'"
            cursor.execute(communityField_sql)
            communityField_data=cursor.fetchall()
            communityInsert = "insert into community values("
            # communityInsert = "insert into community values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            for i in range(len(communityField_data)):
                communityFieldName.append(communityField_data[i].get('COLUMN_NAME'))
                if i!=len(communityField_data)-1:
                    communityInsert += '%s,'
                else:
                    communityInsert += '%s'
            communityInsert += ')'
            community_sql = "select communityID from community where communityID=%s"
            house_sql = "select houseID from eachhouse where houseID=%s"
            for value in url_lis:
                if not cursor.execute(house_sql, value.get('houseID')):
                    stopTime = random.uniform(1,2)
                    time.sleep(stopTime)
                    jingtaiRes = get_jingtai_data([value.get('houseurl'),value.get('area')])
                    if not jingtaiRes: # 有一些房子没有房屋总价，或者爬取不到小区ID，所以我没有要这样的数据，返回空
                        continue
                    communitylis=[]
                    if not cursor.execute(community_sql, jingtaiRes['communityID']): # 如果没有这个小区就插入
                        stopTime = random.uniform(1,2)
                        time.sleep(stopTime)
                        communityRes = get_community_data(jingtaiRes['小区详情url'])  
                        try:     
                            for Name in communityFieldName:
                                communitylis.append(communityRes.get(Name,'NULL'))
                            cursor.execute(communityInsert, communitylis)
                            del communitylis[0]
                            del communitylis[0]
                            conn.commit()
                        except:
                            errorFile = open('errorlog.txt', 'a')
                            errorFile.write(f"================{time.asctime()}=================")
                            errorFile.write(traceback.format_exc())
                            errorFile.close()
                    else :
                        get_community_sql = "select * from community where communityID=%s"
                        cursor.execute(get_community_sql, jingtaiRes['communityID'])
                        communityRes=cursor.fetchall()[0]
                        communityRes.pop('crawlingTime')
                        communityRes.pop('communityID')
                        for Name in list(communityRes.keys()):
                            communitylis.append(communityRes.get(Name,'NULL'))
                    if communitylis==[]:
                        continue
                    cursor.execute(houseInsert, [jingtaiRes.get('houseID','NULL'),jingtaiRes.get('communityID','NULL'),
                                        datetime.datetime.strptime(jingtaiRes.get('挂牌时间',datetime.datetime.now()), "%Y-%m-%d"),
                                        jingtaiRes.get('房屋总价','NULL'),jingtaiRes.get('房屋每平米价','NULL'),
                                        jingtaiRes.get('建楼时间','NULL'),
                                        jingtaiRes.get('房屋户型','NULL'),jingtaiRes.get('所在楼层','NULL'),
                                        jingtaiRes.get('建筑面积','NULL'),jingtaiRes.get('户型结构','NULL'),
                                        jingtaiRes.get('套内面积','NULL'),jingtaiRes.get('建筑类型','NULL'),
                                        jingtaiRes.get('房屋朝向','NULL'),jingtaiRes.get('建筑结构','NULL'),
                                        jingtaiRes.get('装修情况','NULL'),jingtaiRes.get('梯户比例','NULL'),
                                        jingtaiRes.get('配备电梯','NULL'),
                                        jingtaiRes.get('交易权属','NULL'),jingtaiRes.get('上次交易','NULL'),
                                        jingtaiRes.get('房屋用途','NULL'),jingtaiRes.get('房屋年限','NULL'),
                                        jingtaiRes.get('产权所属','NULL'),jingtaiRes.get('抵押信息','NULL'),
                                        jingtaiRes.get('房本备件','NULL'),jingtaiRes.get('户型分间','NULL'),
                                        jingtaiRes.get('小区详情url','NULL'),jingtaiRes.get('area','NULL')]+communitylis)
                    conn.commit()
            logFile = open('crawlerlog.txt', 'a')
            logFile.write(f"================{time.asctime()}=================\n")
            logFile.write(f'{time.asctime()}七天前数据更新完毕')
            logFile.write("\n")
            logFile.close()
    except:
        errorFile = open('errorlog.txt', 'a')
        errorFile.write(f"================{time.asctime()}=================")
        errorFile.write(traceback.format_exc())
        errorFile.close()
    finally:
        close_conn(conn, cursor)  
def update_data():
    try:
        cursor = None
        conn = None
        conn, cursor = get_conn()
        time_sql = "SELECT DISTINCT listingTime FROM eachhouse ORDER BY listingTime ASC LIMIT 1"
        cursor.execute(time_sql)
        data=cursor.fetchall()
        try:
            if int((datetime.datetime.now()-data[0].get('listingTime')).days) > 90:
                del_sql="DELETE FROM eachhouse WHERE listingTime=%s"
                cursor.execute(del_sql,data[0].get('listingTime'))
                conn.commit()
        except:
            pass
        url_lis = getUrl() 
        logFile = open('crawlerlog.txt', 'a')
        logFile.write(f"================{time.asctime()}=================\n")
        logFile.write(f'{time.asctime()}房屋数据开始更新')
        logFile.write("\n")
        logFile.close()
        houseFieldName=[]
        houseField_sql = "SELECT COLUMN_NAME FROM information_schema.`COLUMNS` WHERE TABLE_NAME = 'eachhouse'"
        cursor.execute(houseField_sql)
        houseField_data=cursor.fetchall()
        houseInsert = "insert into eachhouse values("
        for i in range(len(houseField_data)):
            houseFieldName.append(houseField_data[i].get('COLUMN_NAME'))
            if i!=len(houseField_data)-1:
                houseInsert += '%s,'
            else:
                houseInsert += '%s'
        houseInsert += ')'
        communityFieldName=[]
        communityField_sql = "SELECT COLUMN_NAME FROM information_schema.`COLUMNS` WHERE TABLE_NAME = 'community'"
        cursor.execute(communityField_sql)
        communityField_data=cursor.fetchall()
        communityInsert = "insert into community values("
        # communityInsert = "insert into community values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
        for i in range(len(communityField_data)):
            communityFieldName.append(communityField_data[i].get('COLUMN_NAME'))
            if i!=len(communityField_data)-1:
                communityInsert += '%s,'
            else:
                communityInsert += '%s'
        communityInsert += ')'
        community_sql = "select communityID from community where communityID=%s"
        for value in url_lis:
            jingtaiRes = get_jingtai_data([value.get('houseurl'),value.get('area')])
            if not jingtaiRes: # 有一些房子没有房屋总价，或者爬取不到小区ID，所以我没有要这样的数据，返回空
                continue
            stopTime = random.uniform(1,2)
            time.sleep(stopTime)
            communitylis=[]
            if not cursor.execute(community_sql, jingtaiRes['communityID']): # 如果没有这个小区就插入
                stopTime = random.uniform(1,2)
                time.sleep(stopTime)
                communityRes = get_community_data(jingtaiRes['小区详情url'])  
                try:     
                    for Name in communityFieldName:
                        communitylis.append(communityRes.get(Name,'NULL'))
                    cursor.execute(communityInsert, communitylis)
                    del communitylis[0]
                    del communitylis[0]
                    conn.commit()
                except:
                    errorFile = open('errorlog.txt', 'a')
                    errorFile.write(f"================{time.asctime()}=================")
                    errorFile.write(traceback.format_exc())
                    errorFile.close()
            else :
                get_community_sql = "select * from community where communityID=%s"
                cursor.execute(get_community_sql, jingtaiRes['communityID'])
                communityRes=cursor.fetchall()[0]
                communityRes.pop('crawlingTime')
                communityRes.pop('communityID')
                for Name in list(communityRes.keys()):
                    communitylis.append(communityRes.get(Name,'NULL'))
            if communitylis==[]:
                continue
            cursor.execute(houseInsert, [jingtaiRes.get('houseID','NULL'),jingtaiRes.get('communityID','NULL'),
                                        datetime.datetime.strptime(jingtaiRes.get('挂牌时间',datetime.datetime.now()), "%Y-%m-%d"),
                                        jingtaiRes.get('房屋总价','NULL'),jingtaiRes.get('房屋每平米价','NULL'),
                                        jingtaiRes.get('建楼时间','NULL'),
                                        jingtaiRes.get('房屋户型','NULL'),jingtaiRes.get('所在楼层','NULL'),
                                        jingtaiRes.get('建筑面积','NULL'),jingtaiRes.get('户型结构','NULL'),
                                        jingtaiRes.get('套内面积','NULL'),jingtaiRes.get('建筑类型','NULL'),
                                        jingtaiRes.get('房屋朝向','NULL'),jingtaiRes.get('建筑结构','NULL'),
                                        jingtaiRes.get('装修情况','NULL'),jingtaiRes.get('梯户比例','NULL'),
                                        jingtaiRes.get('配备电梯','NULL'),
                                        jingtaiRes.get('交易权属','NULL'),jingtaiRes.get('上次交易','NULL'),
                                        jingtaiRes.get('房屋用途','NULL'),jingtaiRes.get('房屋年限','NULL'),
                                        jingtaiRes.get('产权所属','NULL'),jingtaiRes.get('抵押信息','NULL'),
                                        jingtaiRes.get('房本备件','NULL'),jingtaiRes.get('户型分间','NULL'),
                                        jingtaiRes.get('小区详情url','NULL'),jingtaiRes.get('area','NULL')]+communitylis)
            conn.commit()
        logFile = open('crawlerlog.txt', 'a')
        logFile.write(f"================{time.asctime()}=================\n")
        logFile.write(f'{time.asctime()}房屋数据更新完毕')
        logFile.write("\n")
        logFile.close()
    except:
        errorFile = open('errorlog.txt', 'a')
        errorFile.write(f"================{time.asctime()}=================")
        errorFile.write(traceback.format_exc())
        errorFile.close()
    finally:
        close_conn(conn, cursor)

def crawlerRun():
    with open("errorlog.txt", 'r+') as file:
        file.truncate(0)
    with open("crawlerlog.txt", 'r+') as file:
        file.truncate(0)
    makeIp()
    update_data()
    makeIp()
    update_count()
    makeIp()
    update_seven()
    with open('/www/wwwroot/test/crawler/crontabtest.log', 'a+') as logfile:
        logfile.write(f"================{time.asctime()}=================")
        logfile.write("执行了爬虫脚本")
        logfile.write("\n")

if __name__=='__main__':
    crawlerRun()
        