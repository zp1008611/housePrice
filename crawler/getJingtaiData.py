from getHtml import get_html
import requests
import json
import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import time
import random
import traceback

def get_user_agent():
    lis=["Mozilla/5.0 (Linux; Android 4.1.1; Nexus 7 Build/JRO03D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Safari/535.19",
    "Mozilla/5.0 (Linux; U; Android 4.0.4; en-gb; GT-I9300 Build/IMM76D) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "Mozilla/5.0 (Linux; U; Android 2.2; en-gb; GT-P1000 Build/FROYO) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0",
    "Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.94 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 4.0.4; Galaxy Nexus Build/IMM76B) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.133 Mobile Safari/535.19",
    "Mozilla/5.0 (iPad; CPU OS 5_0 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9A334 Safari/7534.48.3",
    "Mozilla/5.0 (iPod; U; CPU like Mac OS X; en) AppleWebKit/420.1 (KHTML, like Gecko) Version/3.0 Mobile/3A101a Safari/419.3"]
    index = random.randint(0,len(lis)-1)
    return lis[index]

#多进程用
def get_jingtai_dict(url,area):
    # userAgent=get_user_agent()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
    }
    html = get_html(url,headers)
    final_dict =dict()
    # 房子ID
    houseID = url.split('/')[-1][:-5]
    final_dict['houseID']=houseID
    # 小区ID
    communityID = ''
    try:
        communityID = html.xpath('//div[@class="content"]/div/@data-lj_action_housedel_id')[0] 
        final_dict['communityID'] = communityID
    except:
        return
    # 房屋关注人数
    # final_dict['关注人数'] = html.xpath('//span[contains(@id, "favCount")]/text()')[0]
    # 房屋总价
    try:
        final_dict['房屋总价'] = eval(html.xpath('//span[contains(@class, "total")]//text()')[0])
    except:
        return
    # 房屋均价
    try:
        final_dict['房屋每平米价'] = int(html.xpath('//span[contains(@class, "unitPriceValue")]//text()')[0])
    except:
        pass

    # 建楼时间
    try:
        final_dict['建楼时间'] = html.xpath('//div[@class="subInfo noHidden"]/text()')[0].split('/')[0]
    except:
        pass
    # # 房屋总价
    # total_price=html.xpath('//div[@class="price"]/span/text()')[0]+'万'
    # # 房屋均价
    # unit_price=html.xpath('//span[@class="unitPriceValue"]/text()')[0]+'元/平米'

    # 基本属性
    # 基本属性的标签:房屋户型、所在楼层、建筑面积、户型结构、套内面积、建筑类型、房屋朝向、建筑结构、装修情况、梯户比例、配备电梯）
    try:
        base_label = html.xpath('//div[@class="base"]//div[@class="content"]/ul/li/span/text()')
        # 基本属性的内容
        base_content = html.xpath('//div[@class="base"]//div[@class="content"]/ul/li/text()')
        base_dic = dict(zip(base_label, base_content))
    except:
        pass
    # 更新基本属性和交易属性入final_dict
    for item in base_dic.items():
        final_dict[item[0]]=item[1]

    # 交易属性
    # 交易属性的标签：挂牌时间、交易权属、上次交易时间、房屋用途、房屋年限、产权所属、抵押信息、房本备件）
    try:
        transaction_label = html.xpath('//div[@class="transaction"]/div[@class="content"]/ul/li/span[position()=1]/text()')
        # 交易属性的内容
        transaction_content = html.xpath(
            '//div[@class="transaction"]/div[@class="content"]/ul/li/span[position()>1]/text()')
        for i in range(len(transaction_content)):
            transaction_content[i] = transaction_content[i].strip()
        transaction_dic = dict(zip(transaction_label, transaction_content))
    except:
        pass
    for item in transaction_dic.items():
        final_dict[item[0]]=item[1]
    # 房源特色
    # 房源特色的标签：房源标签，核心卖点，小区介绍，周边配套，交通出行...
    # 房源标签
    # House_tags = html.xpath('//div[@class = "tags clear"]//a/text()')
    # for i in range(len(House_tags)):
    #     House_tags[i] = House_tags[i].strip()
    # final_dict['tag'] = House_tags
    # # 核心卖点，小区介绍，周边配套，交通出行的爬取...
    # # theme_list = ['核心卖点', '小区介绍', '周边配套', '交通出行', '户型介绍', '装修描述']
    # # Key_selling_points, introduction, SurroundingFacilities, traffic, House_type, renovation
    # Content_list = []
    # for i in range(len(theme_list)):
    #     try:
    #         Content_list.append(
    #             html.xpath('//div[text()=$val]/following-sibling::*[1]/text()', val=theme_list[i])[0].strip())
    #     except IndexError:
    #         Content_list.append(None)
    # Key_selling_points, introduction, SurroundingFacilities, traffic, House_type, renovation = Content_list
    # final_dict['核心卖点'] = Key_selling_points
    # final_dict['小区介绍'] = introduction
    # final_dict['周边配套'] = SurroundingFacilities
    # final_dict['交通出行'] = traffic
    # final_dict['户型介绍'] = House_type
    # final_dict['装修描述'] = renovation

    # 房屋照片数量
    # try:
    #     Pic_counts = html.xpath('//div[@class="list"]/div/@data-index')[-1]
    # except IndexError:
    #     Pic_counts = None
    # final_dict['房屋图片数量'] = Pic_counts

    # 户型分间
    try:
        all_text = html.xpath('//div[contains(@id, "infoList")]//div[@class = "col"]/text()')
        house_dict = {}
        for i in range(0, len(all_text), 4):
            house_dict[all_text[i]] = [all_text[i + 1], all_text[i + 2], all_text[i + 3]]
        final_dict['户型分间'] = str(house_dict)
    except:
        pass

    # 近7天和30天看房人数
    # r2 = requests.get('https://gz.lianjia.com/ershoufang/houseseerecord?id=' + ID, headers=headers)
    # pycontent = json.loads(r2.text)
    # result = pycontent['data']
    # final_dict['近七天带看房次数'] = result['thisWeek']
    # final_dict['30天带看房次数'] = result['totalCnt']
    # final_dict['爬取日期'] = datetime.date.today()

    # 正则做法
    # 近7天看房次数
    # r2 = (requests.get('https://gz.lianjia.com/ershoufang/houseseerecord?id=' + ID, headers=headers)).text
    # final_dict['近七天带看房次数'] = (re.search('"thisWeek":(.*?),', r2, re.S)).group(1)
    # 近30天看房次数
    # final_dict['30天带看房次数'] = (re.search('"totalCnt":(.*?),', r2, re.S)).group(1)
    # 爬取日期
    # final_dict['爬取日期'] = datetime.date.today()

    # 小区详细信息
    # r3 = requests.get("https://gz.lianjia.com/ershoufang/housestat?hid={0}&rid={1}".format(houseID, communityID),
    #                 headers=headers)
    # pycontent = json.loads(r3.text)
    # result = pycontent['data']['resblockCard']
    try:
        final_dict['小区详情url'] = 'https://gz.lianjia.com/xiaoqu/'+ communityID + '/'
    except:
        pass
    final_dict['area'] = area

    
    
    # dic_series = pd.Series(final_dict)
    #print(final_dict)
    return final_dict

def get_jingtai_data(url_lis):
    # 多线程
    # MAX_WORKER_NUM = multiprocessing.cpu_count()
    # futures=[]
    # with ProcessPoolExecutor(MAX_WORKER_NUM) as pool:
    #     for url in url_lis:
    #         try:
    #             # print(item[0],item[2])
    #             futures.append(pool.submit(get_jingtai_dict))
    #         except:
    #             print('wrong1=============================',futures.index(url))
    #             continue 
    # for j in futures:
    #     try:
    #         res = j.result()
    #         key = res[0]
    #         value = res[1]
    #         data_dic[key] = value
    #     except:
    #         print('wrong2=============================',futures.index(j))
    #         continue 

    try:
        # print(item[0],item[2])
        # futures.append(pool.submit(get_jingtai_dict))
        res_dic = get_jingtai_dict(url_lis[0],url_lis[1])
        return res_dic
    except:
        errorFile = open('errorlog.txt', 'a')
        errorFile.write(f"================{time.asctime()}=================")
        errorFile.write(traceback.format_exc())
        errorFile.write(url_lis[0])
        errorFile.close()

# if __name__=='__main__':
#     dic = get_jingtai_dict('https://gz.lianjia.com/ershoufang/108402692493.html',0)
#     print(dic)
    