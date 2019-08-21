#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
@author: 罗兴红
@contact: EX-LUOXINGHONG001@pingan.com.cn
@file: test.py
@time: 2019/7/24 10:19
@desc:
'''
import requests

proxies = {
    "http": "http://91.121.162.173:80",
    "https": "http://114.116.75.60:25695",
}
tieba_url = "http://tieba.baidu.com/p/6203615879"

requests.packages.urllib3.disable_warnings()
req = requests.get(tieba_url, proxies=proxies, timeout=30, verify=False)  # http
print(req)
