from urllib.parse import urlencode
import queue
import math
import datetime
import random
import time
import json

import requests

from config import COOKIE, AREA_CODE, KIND


headers = {
    'Host': 'index.baidu.com',
    'Connection': 'keep-alive',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
}


class BaiduIndex:
    # 切分关键词list，每5个一组
    def split_keywords(self, keywords: list) -> [list]:
        return [keywords[i*5: (i+1)*5] for i in range(math.ceil(len(keywords)/5))]

    # 切分时间段
    def get_time_range_list(self, start, end):
        dates_list = []
        start_date = datetime.datetime.strptime(start, '%Y-%m-%d')
        end_date = datetime.datetime.strptime(end, '%Y-%m-%d')
        while 1:
            temp_date = start_date + datetime.timedelta(days=300)
            if temp_date > end_date:
                dates_list.append((start_date, end_date))
                break
            dates_list.append((start_date, temp_date))
            start_date = temp_date + datetime.timedelta(days=1)
        return dates_list

    def init_params(self, start_date, end_date, keywords):
        http_params = queue.Queue()
        keywords_list = self.split_keywords(keywords)
        dates_list = self.get_time_range_list(start_date, end_date)
        for start_date, end_date in dates_list:
            for keywords in keywords_list:
                params = {
                    'keywords': keywords,
                    'start_date': start_date,
                    'end_date': end_date
                }
                http_params.put(params)
        return http_params
        
    def __init__(self, keywords: list, start_date: str, end_date: str):
        self.keywords = keywords
        self.http_params = self.init_params(start_date, end_date, keywords)


    def get_encrypt_datas(self, start_date, end_date, keywords):
        request_args = {
            'word': ','.join(keywords),
            'startDate': start_date.strftime('%Y-%m-%d'),
            'endDate': end_date.strftime('%Y-%m-%d'),
            'area': AREA_CODE[self.area]
        }
        url = 'http://index.baidu.com/api/SearchApi/index?' + \
            urlencode(request_args)
        html = self.http_get(url)
        datas = json.loads(html)
        uniqid = datas['data']['uniqid']
        encrypt_datas = []
        for single_data in datas['data']['userIndexes']:
            encrypt_datas.append(single_data)
        return (encrypt_datas, uniqid)

    def get_key(self, uniqid):
        url = 'http://index.baidu.com/Interface/api/ptbk?uniqid=%s' % uniqid
        html = self.http_get(url)
        datas = json.loads(html)
        key = datas['data']
        return key

    # 把数据格式化成输出的形式
    def format_data(self, data):
        keyword = str(data['word'])
        time_length = len(data['all']['data'])
        start_date = data['all']['startDate']
        cur_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        for i in range(time_length):
            for kind in KIND:
                index_datas = data[kind]['data']
                index_data = index_datas[i] if len(
                    index_datas) != 1 else index_datas[0]
                formated_data = {
                    'keyword': keyword,
                    'type': KIND[kind],
                    'date': cur_date.strftime('%Y-%m-%d'),
                    'area': self.area,
                    'index': index_data if index_data else '0'
                }
                yield formated_data
            cur_date += datetime.timedelta(days=1)

    def http_get(self, url, cookies=COOKIE):
        headers['Cookie'] = cookies
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code != 200:
            raise requests.Timeout
        return response.text
        
    # 对某个关键词，得到一个串，这个串表示这种kind下所有日期下的index
    def decrypt(self, key, data):
        a = key
        i = data
        n = {}
        s = []
        for o in range(len(a)//2):
            n[a[o]] = a[len(a)//2 + o]
        for r in range(len(data)):
            s.append(n[i[r]])
        return ''.join(s).split(',')

    # 单账号抓取过快会掉线，简易地反反爬虫
    def sleep(self):
        sleep_time = random.choice(range(50, 90)) * 0.1
        time.sleep(sleep_time)

    def get_index(self):
        while True:
            try:
                params_data = self.http_params.get(timeout=1)
                for area in AREA_CODE:
                    self.area = area
                    encrypt_datas, uniqid = self.get_encrypt_datas(
                        start_date=params_data['start_date'],
                        end_date=params_data['end_date'],
                        keywords=params_data['keywords']
                    )
                    key = self.get_key(uniqid)
                    for encrypt_data in encrypt_datas:
                        for kind in KIND:
                            encrypt_data[kind]['data'] = self.decrypt(
                                key, encrypt_data[kind]['data'])
                        for formated_data in self.format_data(encrypt_data):
                            yield formated_data
            except requests.Timeout:
                self.http_params.put(params_data)
            except queue.Empty:
                break
            self.sleep()

