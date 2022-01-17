import requests
from lxml import etree
import time
import json
import random

class Make_IP(object):
    def __init__(self):
        self.start_url='https://www.kuaidaili.com/free/inha/{}/'
        self.headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"
        }

    def get_ip(self):
        proxies_lis = []
        #这里的数量可以自己定，要爬多少代理IP自己定
        for i in range(1,10):
            url=self.start_url.format(i)
            response=requests.get(url,headers=self.headers)
            content=response.content.decode('utf8')
            html=etree.HTML(content)

            #代理IP格式  {"ip的协议":'ip:ip的端口'}
            #爬取ip

            trs=html.xpath('//tbody/tr')
            for tr in trs:
                proxies_dict={}
                http_type=tr.xpath('./td[4]/text()')[0]
                ip_num=tr.xpath('./td[1]/text()')[0]
                ip_port=tr.xpath('./td[2]/text()')[0]
                proxies_dict[http_type]=ip_num+':'+ip_port
                proxies_lis.append(proxies_dict)
            time.sleep(1)
        return proxies_lis

    def check_ip(self,proxies_lis):
        can_ues=[]
        for proxy in proxies_lis:
            #如果能在0.1秒内返回则不会报错
            try:
                response=requests.get('https://www.baidu.com',headers=self.headers,
                            proxies=proxy,timeout=0.1)
                if response.status_code==200:
                    can_ues.append(proxy)
            except Exception as e:
                print(proxy,e)
        return can_ues

def makeIp():
    make_ip=Make_IP()
    proxies_lis=make_ip.get_ip()
    can_use=make_ip.check_ip(proxies_lis)
    print(len(can_use))
    with open('ip.txt', 'w') as file:
        json.dump(can_use,file)




