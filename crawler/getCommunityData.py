from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import  time
import numpy as np
import re
import pandas as pd
# from multiprocessing.dummy import Pool
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import datetime
import random
import traceback
from getHtml import get_proxie 
from getHtml import get_html


# headers = {
#     "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
# }

#下面的大学，医院去重中，需要用到
def remove_duplicate(facility,title_lis, distance_lis):
    f = facility
    for i in range(len(title_lis)):
        try:
            university = re.search('(.*?' + '{})'.format(f), title_lis[i]).group(1)
            title_lis[i] = university
        except AttributeError:
            pass
    element_dic = {"name": title_lis, "distance": distance_lis}
    fundata = pd.DataFrame(element_dic)
    fundata.drop_duplicates(subset=['name'], keep='first', inplace=True)
    # print("去重后:", list(fundata['name']))
    ave_distance = fundata['distance'].mean()
    return ave_distance, fundata

# def get_user_agent():
#     lis=["Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19",
#     "Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
#     "Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
#     "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0",
#     "Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0",
#     "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
#     "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19",
#     "Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3",
#     "Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3"]
#     index = random.randint(0,len(lis)-1)
#     return lis[index]

#数据爬取
def get_dongtai_dic(url):
    options = Options()
    options.add_argument('--no-sandbox')
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-dev-shm-usage')
    options.add_experimental_option('excludeSwitches', ['enable-automation'])
    # userAgent = get_user_agent()
    # options.add_argument('user-agent={}'.format(userAgent)) #修改user agent
    # wdip = 'http://'+get_proxie(-1).get('HTTP')
    # options.add_argument("--proxy-server={}".format(wdip))
    wd = webdriver.Chrome(options=options)
    wd.implicitly_wait(5)
    wd.get(url)
    # print(wd.execute_script("return navigator.userAgent"))
    time.sleep(0.5)
    wd.execute_script('var q=document.documentElement.scrollTop=5500')
    facility_dic={}
    #交通：地铁和公交的线路数也算一个特征，所以分开爬
    #教育：因为教育中的大学板块中有一些元素的地址是重复，如（华南师范大学，华南师范大学-产业大楼），需要特别处理，所以分开爬
    #医疗：因为医疗中的医院版块中有一些元素的地址是重复，如（某医院，某医院-内科楼，某医院-外科楼），需要特别处理，所以分开爬

    kinds=['traffic','education','medical','shopping','life','entertainment']
    f_dict={"subway":"地铁","bus":"公交","kindergarten":"幼儿园","primary-school":"小学","middle-school":"中学",
            "University":"大学","hospital":"医院","pharmacy":"药店","mall":"商场","supermarket":"超市","market":"市场",
            "bank":"银行", "atm":"ATM", "restaurant":"餐厅", "coffee":"咖啡馆",
            "park":"公园", "cinema":"电影院", "gym":"健身房", "sport":"体育馆"}
    dic={'traffic':["subway","bus"],
            'education':["kindergarten","primary-school","middle-school","University"],
            'medical':["hospital","pharmacy"],
            'shopping':["mall","supermarket","market"],
            'life':["bank","atm","restaurant","coffee"],
            'entertainment':["park","cinema","gym","sport"]}    
    #交通
    traffic_buttom = wd.find_element_by_css_selector('[data-bl={}]'.format('traffic'))
    wd.execute_script("arguments[0].click();", traffic_buttom)
    for facility in dic['traffic']:
        try:
            #获取地铁和公交在列表中的索引，因为第一个是不用按的
            index=dic['traffic'].index(facility)
            #如果不是第一个就要按
            if index!=0:
                facility_buttom = wd.find_element_by_css_selector('[data-bl={}]'.format(facility))
                wd.execute_script("arguments[0].click();", facility_buttom)
            elements = wd.find_elements_by_css_selector('.contentBox')

            distance_lis=[]
            for element in elements:
                distance = element.find_element_by_class_name('itemdistance').text
                distance_lis.append(eval(distance[:-1]))

            if len(distance_lis)>0:#如果distance_lis是空的，则会报错
                ave_distance=np.array(distance_lis).mean()
            else:
                ave_distance=0
            facility_dic['{}站数'.format(f_dict[facility])]=len(elements)
            facility_dic['{}平均距离'.format(f_dict[facility])]=int(ave_distance)
        except:
            errorFile = open('crawlerlog.txt', 'a')
            errorFile.write(f"================{time.asctime()}=================")
            errorFile.write(traceback.format_exc())
            errorFile.write(url)
            errorFile.close()

    # 教育，医疗，购物，生活，娱乐
    for kind in kinds[1:]:
        buttom = wd.find_element_by_css_selector('[data-bl={}]'.format(kind))
        wd.execute_script("arguments[0].click();", buttom)
        for facility in dic[kind]:
            try:
                # 获取地铁和公交在列表中的索引，因为第一个是不用按的
                index = dic[kind].index(facility)
                # 如果不是第一个就要按
                if index != 0:
                    facility_buttom = wd.find_element_by_css_selector('[data-bl={}]'.format(facility))
                    wd.execute_script("arguments[0].click();", facility_buttom)
                elements = wd.find_elements_by_css_selector('.contentBox')
                distance_lis = []
                if facility in ["University","hospital"]:
                    title_lis = []
                    for element in elements:
                        title_lis.append(element.find_element_by_class_name('itemTitle').text)
                        distance = element.find_element_by_class_name('itemdistance').text
                        distance_lis.append(eval(distance[:-1]))  # 把'米'去掉
                    # print("去重前:",title_lis)
                    ave_distance, data = remove_duplicate(f_dict[facility], title_lis, distance_lis)
                    facility_dic['{}数'.format(f_dict[facility])] = len(data['name'])
                    if(np.isnan(ave_distance)):
                        ave_distance = 0
                    facility_dic['{}平均距离'.format(f_dict[facility])] = int(ave_distance)

                elif facility not in ["University","hospital"]:
                    for element in elements:
                        distance = element.find_element_by_class_name('itemdistance').text
                        distance_lis.append(eval(distance[:-1]))
                    if len(distance_lis) > 0:  
                        ave_distance = np.array(distance_lis).mean()
                    else:
                        ave_distance = 0
                    facility_dic['{}数'.format(f_dict[facility])] = len(elements)
                    facility_dic['{}平均距离'.format(f_dict[facility])] = int(ave_distance)
            except:
                errorFile = open('crawlerlog.txt', 'a')
                errorFile.write(f"================{time.asctime()}=================")
                errorFile.write(traceback.format_exc())
                errorFile.write(url)
                errorFile.close()
    # facility_dic['小区详情url']=url
    # dic_serise=pd.Series(facility_dic)
    wd.quit()
    return facility_dic

def get_community_data(url):
    # 多线程用
    # MAX_WORKER_NUM = multiprocessing.cpu_count()
    # futures=[]
    # with ProcessPoolExecutor(MAX_WORKER_NUM) as pool:
    #     for url in url_lis:
    #         try:
    #             # print(item[0],item[2])
    #             futures.append(pool.submit(get_dongtai_dic))
    #         except:
    #             print('wrong1=============================',futures.index(url))
    #             continue 
    # for j in futures:
    #     try:
    #         res = j.result()
    #         communityKey = res[0]
    #         communityValue = res[1]
    #         community_dic[communityKey] = communityValue
    #     except:
    #         print('wrong2=============================',futures.index(j))
    #         continue 
    try:
        res = get_dongtai_dic(url)
        communityDic = dict()
        #各设施数量
        communityDic['communityID']=url.split('/')[-2]
        communityDic['crawlingTime'] = datetime.date.today()-datetime.timedelta(days=0)
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }
        stopTime = random.uniform(1,2)
        time.sleep(stopTime)
        communityHtml = get_html(url, headers)
        # communityDESC = communityHtml.xpath('//div[@class="xiaoquInfo"]')[0]
        try:
            communityDic['communityAvePrice'] = int(communityHtml.xpath('//span[@class="xiaoquUnitPrice"]/text()')[0])
        except:
            pass
        try:
            communityDic['communityBuildingsYear'] = int(communityHtml.xpath('//div[@class="xiaoquInfo"]//span[@class="xiaoquInfoContent"]/text()')[0].split('年')[0])
        except:
            pass
        try:
            communityDic['communityBuildingsType'] = communityHtml.xpath('//div[@class="xiaoquInfo"]//span[@class="xiaoquInfoContent"]/text()')[1]
        except:
            pass
        try:
            communityDic['communityPropertyFee'] = communityHtml.xpath('//div[@class="xiaoquInfo"]//span[@class="xiaoquInfoContent"]/text()')[2]
        except:
            pass
        try:
            communityDic['communityBuildingsNum'] = int(communityHtml.xpath('//div[@class="xiaoquInfo"]//span[@class="xiaoquInfoContent"]/text()')[-3].split('栋')[0])
        except:
            pass
        try:
            communityDic['communityHouseNum'] = int(communityHtml.xpath('//div[@class="xiaoquInfo"]//span[@class="xiaoquInfoContent"]/text()')[-2].split('户')[0])
        except:
            pass
        communityDic['educationNum'] = int(res.get('幼儿园数',0)+res.get('小学数')+res.get('中学数',0)+res.get('大学数',0))
        communityDic['trafficNum'] = int(res.get('地铁站数',0)+res.get('公交站数',0))
        communityDic['shoppingNum'] = int(res.get('商场数',0)+res.get('超市数',0)+res.get('市场数',0))
        communityDic['lifeNum'] = int(res.get('银行数',0)+res.get('ATM数',0)+res.get('餐厅数',0)+res.get('咖啡馆数',0))
        communityDic['entertainmentNum'] = int(res.get('公园数',0)+res.get('电影院数',0)+res.get('健身房数',0)+res.get('体育馆数',0))
        communityDic['medicalNum'] = int(res.get('医院数',0)+res.get('药店数',0))
        #各设施平均距离
        communityDic['educationDistance'] = int((res.get('幼儿园平均距离',0)+res.get('小学平均距离',0)+res.get('中学平均距离',0)+res.get('大学平均距离',0))/4)
        communityDic['trafficDistance'] = int((res.get('地铁平均距离',0)+res.get('公交平均距离',0))/2)
        communityDic['shoppingDistance'] = int((res.get('商场平均距离',0)+res.get('超市平均距离',0)+res.get('市场平均距离',0))/3)
        communityDic['lifeDistance'] = int((res.get('银行平均距离',0)+res.get('ATM平均距离',0)+res.get('餐厅平均距离',0)+res.get('咖啡馆平均距离',0))/4)
        communityDic['entertainmentDistance'] = int((res.get('公园平均距离',0)+res.get('电影院平均距离',0)+res.get('健身房平均距离',0)+res.get('体育馆平均距离',0))/4)
        communityDic['medicalDistance'] = int((res.get('医院平均距离',0)+res.get('药店平均距离',0))/2)
        
        return communityDic
    except:
        errorFile = open('errorlog.txt', 'a')
        errorFile.write(f"================{time.asctime()}=================")
        errorFile.write(traceback.format_exc())
        errorFile.write(url)
        errorFile.close()

if __name__=='__main__':
    dic = get_community_data('https://gz.lianjia.com/xiaoqu/219980390419828/')
    print(dic)
# if __name__=='__main__':
#     a=get_community_data('https://gz.lianjia.com/xiaoqu/2120022444145792/')
#     print(a)
    # wd = webdriver.Chrome(r'D:/Python/Scripts/chromedriver.exe')
    # start = time.clock()
    # urls=pd.read_excel('each information.xlsx')['小区详情url'].unique()
    # url_list = list(urls[:3])
    # MAX_WORKER_NUM = multiprocessing.cpu_count()
    # p = Pool(MAX_WORKER_NUM)
    # data_lis = p.map(get_data, url_list)
    # """map(func, iterable, chunksize=None) method of multiprocessing.pool.Pool instance
    # Apply `func` to each element in `iterable`, collecting the results
    # in a list that is returned."""
    # p.close()

    # mydf = pd.DataFrame(data_lis)
    # mydf.to_excel('小区周边.xlsx', index=None)
    # end = time.clock()
    # print(end - start)