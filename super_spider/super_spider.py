import requests
import json
from jsonpath import jsonpath
from lxml import etree
from scrapy.linkextractors import LinkExtractor
import pandas as pd
import re
import time
import super_spider_run
import sys


with open('super_spider_config.json', 'r', encoding='utf-8') as f:
    config_data = f.read()
    config_data = json.loads(config_data)


headers = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit'
                      '/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
}
if config_data['headers_other_data'] != {}:
    headers.update(config_data['headers_other_data'])

method = config_data['method']


class SuperSpider(object):
    def __init__(self, res_url, post_data):
        self.url = res_url
        self.post_data = post_data
        if method == 'get' or method == 'GET':
            self.res_method = requests.get(self.url, headers=headers)
        if method == 'post' or method == 'POST':
            self.res_method = requests.post(self.url, headers=headers, data=self.post_data)

    # get请求方式
    def get_requests(self):
        html = etree.HTML(self.res_method.content.decode())
        return html

    # post请求方式
    def post_requests(self):
        json_data = json.loads(self.res_method.content.decode())
        return json_data

    # 暂时废弃
    def parse(self, response):
        link = LinkExtractor(allow=r'/page/\d+.html')
        link_list = link.extract_links(response)
        return link_list

    # 链接生成器
    def link_generator(self, link, quantity):
        for i in range(int(quantity)):
            # 写好格式化链接 带%s
            new_link = str(link) %(i)
            yield new_link


# 实例化
def instantiation(in_sec_url):
    if config_data['urls'] == '':
        print('请将url填写完整！')
        sys.exit()
    if config_data['method'] == '':
        print('请将method填写完整！')
        sys.exit()
    if config_data['down_name'] == '':
        print('请将文件名填写完整！')
        sys.exit()
    print('正在访问目标地址，请稍后！')
    # 判断是不是初始url
    if in_sec_url !='0':
       urls = in_sec_url
    else:
       urls = config_data['urls']
    print(urls)
    data = config_data['data']
    if data == '':
        data = None

    all_data = {}
    conter = 0
    for url in urls:
        spider = SuperSpider(url, data)
        print('访问完毕。')
        print('===========================')
        timeout = config_data['timeout']
        time.sleep(int(timeout))
        res = ''
        if config_data['method'] == 'get' or config_data['method'] == 'GET':
            res = spider.get_requests()
        if config_data['method'] == 'post' or config_data['method'] == 'POST':
            res = spider.post_requests()
        second_url = super_spider_run.change(res)
        second_instructions = input('请确认是否需要下载（y/n）')
        if second_instructions == 'y':
            download(config_data['down_name'], super_spider_run.down_data)
        if second_url != '0':
            second_method = super_spider_run.second_method
            for se_u in second_url:
                response_second_data = ''
                if second_method == 'get' or second_method == 'GET':
                    response_second = requests.get(se_u, headers=headers)
                    response_second_data = etree.HTML(response_second.content.decode())
                if second_method == 'post' or second_method == 'POST':
                    response_second = requests.post(se_u, headers=headers)
                    response_second_data = json.loads(response_second.content.decode())
                print(se_u)
                res_sec_da = super_spider_run.second_requests(response_second_data)
                conter = conter + 1
                if conter == 1:
                    all_data = res_sec_da
                else:
                    for key in res_sec_da.keys():
                        all_data[key].extend(res_sec_da[key])
                print(all_data)
    second_instructions = input('请确认是否需要下载（y/n）')
    if second_instructions == 'y':
        download('详情页数据', all_data)


# 修改json文件模块
def json_update(up_da):
    with open('super_spider_config.json', 'r') as f:
        load_data = json.loads(f.read())
        load_data['urls'] = up_da
    with open('super_spider_config.json', 'w') as f1:
        json.dump(load_data, f1)


# 下载模块
def download(filename, down):
    df = pd.DataFrame(down)
    print(down)
    df.to_excel('excel目录/'+filename+'.xlsx', index=False)
    print("下载完毕请前往 excel目录 文件夹查看。")


if __name__ == '__main__':
    instantiation('0')









