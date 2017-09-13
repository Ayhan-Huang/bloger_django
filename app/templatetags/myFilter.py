#! user/bin/env python
# -*- coding: utf-8 -*-
# __author__ = 'Ayhan_Huang'
from datetime import datetime
from django import template
register = template.Library()
# 导入template 并实例化一个对象，命名为 register

@register.filter  # 装饰自定义函数为过滤器
def date_to_now(raw_datetime):
    # 用户的穿件时间是要给datetime对象
    now = datetime.utcnow().date()
    diff = (now - raw_datetime.date()).days    # 两个datetime对象相减，.days()方法返回间隔天数
    # print('diff---',diff)
    res = divmod(diff, 365)
    y=0
    m=0
    if res[0]:
        y = res[0]
    # print(res[0])
    if res[1]:
        # print(res[1])
        m = res[1]//30
        if m == 0:
            m +=1
    return ('{y}年{m}个月'.format(y=y,m=m))

#
# b =datetime(2015,7,11)
# print(date_to_now(b))