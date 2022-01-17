from getHtml import get_html
import datetime
import random
import time
import traceback
from conn import get_conn,close_conn
def getDayUrl():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    areadic={'天河':'tianhe','越秀':'yuexiu','荔湾':'liwan','海珠':'haizhu','番禺':'panyu','白云':'baiyun','黄埔':'huangpugz','从化':'conghua','增城':'zengcheng','花都':'huadou','南沙':'nansha'}
    DayUrl_dic=dict()
    for tup in list(areadic.items())[:]:
        try:
            stopTime = random.uniform(1,2)
            time.sleep(stopTime)
            url='https://gz.lianjia.com/ershoufang/{}/co32/'.format(tup[1])
            html=get_html(url,headers)
            #信息获取
            trs = html.xpath('//ul[@class="sellListContent"]/li')
            for tr in trs:
                houseurl = tr.xpath('.//div[@class="title"]/a/@href')[0]
                ID = houseurl.split('/')[-1][:-5]
                ds = tr.xpath('.//div[@class="followInfo"]/text()')[0].split('/')[1].strip()
                price = eval(tr.xpath('.//div[@class="totalPrice totalPrice2"]/span/text()')[0])
                avePrice = tr.xpath('.//div[@class="unitPrice"]/span/text()')[0]
                nums = avePrice.split('元')[0].split(',')
                avePrice = int(nums[0])*1000 + int(nums[1])
                if(ds == '刚刚发布'):
                    ds = datetime.date.today()-datetime.timedelta(days=0)
                    DayUrl_dic[ID]={ 'releaseTime':ds, 'area':tup[0], 'price':price, 'avePrice':avePrice, 'houseurl':houseurl} 
                    # {房子ID:{'发布时间':ds, '所在区域':area, '总价':price}}
        except:
            errorFile = open('crawlerlog.txt', 'a')
            errorFile.write(traceback.format_exc())
            errorFile.write(url)
            errorFile.close()
    return DayUrl_dic

def getUrl():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    areadic={'天河':'tianhe','越秀':'yuexiu','荔湾':'liwan','海珠':'haizhu','番禺':'panyu','白云':'baiyun','黄埔':'huangpugz','从化':'conghua','增城':'zengcheng','花都':'huadou','南沙':'nansha'}
    url_lis=[]
    for tup in list(areadic.items()):
        cursor = None
        conn = None
        conn, cursor = get_conn()
        house_sql = "select houseID from eachhouse where houseID=%s"
        try:
            stopTime = random.uniform(1,2)
            time.sleep(stopTime)
            url='https://gz.lianjia.com/ershoufang/{}/'.format(tup[1])
            html=get_html(url,headers)
            #信息获取
            trs = html.xpath('//ul[@class="sellListContent"]/li')
            for tr in trs:
                houseurl = tr.xpath('.//div[@class="title"]/a/@href')[0]
                ID = houseurl.split('/')[-1][:-5]
                if not cursor.execute(house_sql, ID):
                    dsstr = tr.xpath('.//div[@class="followInfo"]/text()')[0].split('/')[1].strip()
                    try:
                        if(dsstr == '刚刚发布'):
                            ds = datetime.date.today()-datetime.timedelta(days=0)
                            url_lis.append({'houseID':ID,'houseurl':houseurl, 'area':tup[0]}) 
                            # {房子ID:{'房子url':houseurl, '发布时间':ds, '所在区域':area, '总价':price}}
                        elif len(dsstr.split('天')) == 1:
                            t = int(dsstr.split('个')[0])
                            if(t<=3):
                                ds = datetime.date.today()-datetime.timedelta(days=t*30)
                                url_lis.append({'houseID':ID,'houseurl':houseurl, 'area':tup[0]}) 
                        elif len(dsstr.split('天')) == 2:
                            t = int(dsstr.split('天')[0])
                            ds = datetime.date.today()-datetime.timedelta(days=t)
                            url_lis.append({'houseID':ID,'houseurl':houseurl, 'area':tup[0]}) 
                    except:
                        pass

        except:
                errorFile = open('errorlog.txt', 'a')
                errorFile.write(traceback.format_exc())
                errorFile.write(url)
                errorFile.close()
        finally:
            close_conn(conn, cursor)
    return url_lis