#!/usr/bin/python
# -*- coding: UTF-8 -*- 
from pypinyin import pinyin, lazy_pinyin
# 不需要声调
py_r = lazy_pinyin(u"没有了诗和远方")
print py_r
 
# 特殊字符
# 默认
py_r = lazy_pinyin(u"满天都是小☆☆")
print py_r
 
# 不理睬，忽略
py_r = lazy_pinyin(u"满天都是小☆☆", errors=u'ignore')
print py_r
 
# 替换
py_r = lazy_pinyin(u"满天都是小☆☆", errors=u'replace')
 
# 也可以使用回调函数处理
py_r = lazy_pinyin(u"满天都是小☆☆", errors=lambda x: 'star')
print py_r
