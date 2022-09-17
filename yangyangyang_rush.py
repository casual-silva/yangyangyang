# -- coding: utf-8 --

# @File : yangyangyang_rush.py
# @Software : PyCharm
# @Author : Silva
# @Time : 2022/9/17 下午9:11

import copy
import requests
import traceback
from functools import wraps
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
requests.packages.urllib3.disable_warnings()

headers = {
    'Host': 'cat-match.easygame2021.com',
    'Connection': 'keep-alive',
    'content-type': 'application/json',
    'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.26(0x18001a34) NetType/WIFI Language/zh_CN',
    'Referer': 'https://servicewechat.com/wx141bfb9b73c970a9/15/page-frame.html',
    't': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJleHAiOjE2OTQ1MDI0NDUsIm5iZiI6MTY2MzQwMDI0NSwiaWF0IjoxNjYzMzk4NDQ1LCJqdGkiOiJDTTpjYXRfbWF0Y2g6bHQxMjM0NTYiLCJvcGVuX2lkIjoiIiwidWlkIjo0NTk0MjYwMiwiZGVidWciOiIiLCJsYW5nIjoiIn0.1lXIcb1WL_SdsXG5N_i1drjjACRhRZUS2uadHlT6zIY'
}

# 异常处理 无线重试
def except_output(msg='异常', retry_num=10, is_while=True):
    '''

    :param msg:
    :param retry_num:
    :param is_while: 是否死循环重试
    :return:
    '''
    # msg用于自定义函数的提示信息
    def except_execute(func):
        @wraps(func)
        def execept_print(*args, **kwargs):
            try:
                print('start:',func.__name__)
                return func(*args, **kwargs)
            except Exception as e:
                sign = '=' * 60 + '\n'
                print(f'{sign}>>>异常时间：\t{datetime.now()}\n>>>异常函数：\t{func.__name__}\n>>>{msg}：\t{e}')
                # print(f'{sign}{traceback.format_exc()}{sign}')
                if is_while:
                    return execept_print(*args, **kwargs)
                else:
                    return None
        return execept_print
    return except_execute

@except_output(msg='fetch_wx_union_id', retry_num=5)
def fetch_wx_union_id(user_id):
    response = requests.get(f"https://cat-match.easygame2021.com/sheep/v1/game/user_info?uid={user_id}", verify=False, headers=headers)
    print(response.json()['data'])
    wx_union_id = response.json()['data']['wx_open_id']
    return wx_union_id

@except_output(msg='fetch_token', retry_num=5)
def fetch_token(wx_union_id):
    tokenUrl = "https://cat-match.easygame2021.com/sheep/v1/user/login_tourist"
    data = {"uuid": wx_union_id}
    res = requests.post(tokenUrl, data, verify=False).json()
    return res['data']['token']


class YangYang:
    '''
    根据游戏id刷通关次数 默认100次
    '''

    def __init__(self, user_id, count=100, max_workers=1000):
        self.user_id = user_id
        self.count = count
        self.sucess_num = 0
        self.all_task = []
        self.is_end = False
        self.pool = ThreadPoolExecutor(max_workers=max_workers)
        print(f'开启线程池size：{max_workers}')

    def get_token_t(self):
        wx_union_id = fetch_wx_union_id(self.user_id)
        print("wx_union_id:", wx_union_id)
        token = fetch_token(wx_union_id)
        print("token:", token)
        return token

    def go_pass(self):
        '''
        通关冲冲冲
        '''
        print(f'user_id:{self.user_id} 开始通关中 ...')
        token  = self.get_token_t()
        while True:
            task = self.pool.submit(self.fetch_pass, token)
            self.all_task.append(task)
            if self.is_end:
                break
        for t in self.all_task:
            t.cancel()

    @except_output(msg='go_pass', retry_num=10, is_while=False)
    def fetch_pass(self, t):
        params = {
            'rank_score': '1',
            'rank_state': '1',
            'rank_time': '40',
            'rank_role': '1',
            'skin': '1',
        }
        __headers = copy.deepcopy(headers)
        __headers['t'] = t
        response = requests.get('https://cat-match.easygame2021.com/sheep/v1/game/game_over', params=params,
                                headers=__headers, verify=False)
        print(response.text)
        self.sucess_num += 1
        print(f'牛哇！user_id:{self.user_id} 通关第: {self.sucess_num} 次成功！')
        if self.sucess_num >= self.count:
            self.is_end = True
            print('通关完成！')

if __name__ == '__main__':
    YangYang('xxxx', count=100).go_pass()
