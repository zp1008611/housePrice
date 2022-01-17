import requests
import pandas as pd
from lxml import etree
import json
import random
# ip_random = -1
import json

#代理接入
def get_proxie(random_number):
    with open('ip.txt', 'r') as file:
        ip_list = json.load(file)
    if random_number == -1:
        random_number = random.randint(0, len(ip_list) - 1)
        proxies=ip_list[random_number]
    # return random_number,proxies
    return proxies


    
#html获取
def get_html(url, headers):
    # 不接代理时注释这一段
    ip_random = -1
    proxies = get_proxie(ip_random)
    print(proxies)
    try:
        response = requests.get(url=url, headers=headers, proxies=proxies, timeout=1)
    except:
        request_status = 500
    else:
        request_status = response.status_code
    while request_status != 200:
        ip_random = -1
        proxies = get_proxie(ip_random)
        try:
            print(proxies)
            response = requests.get(url=url, headers=headers, proxies=proxies, timeout=1)
        except:
            request_status = 500
        else:
            request_status = response.status_code
    # ip_random = ip_rand
    
    # response = requests.get(url, headers=headers)
    content = response.content.decode('utf8')
    # etree解析
    html = etree.HTML(content)
    return html

if __name__=='__main__':
    print('http://'+get_proxie(-1).get('HTTP'))