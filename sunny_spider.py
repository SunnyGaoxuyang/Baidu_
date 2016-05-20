#!/usr/bin/python
# coding: utf-8
"""
    作者: 高旭阳 from 电子科技大学
    Github：SunnyGaoxuyang
    版本: 1.0.1 中文测试版
    时间: 2016.4.27
    功能 : 爬取百度新闻所有 "电子科技大学" 相关的新闻， 包含 新闻标题-来源&时间-内容-链接

    备注:
    1. 该版本为单线程版本，运行速度较慢，为了保证能完整爬取，使用了try语法，尽管这个措施进一步降低了速度
    2. 本脚本为SunnySpiderNLP框架的原型测试脚本，该框架在整合自然语言处理及网络爬虫，即将发布于Github，敬请关注
    3. 本代码仅限内部人员交流使用，未经作者允许不可外传，否则视为愿意向作者支付 2人民币/字符 的转载费

"""
__author__ = 'SunnyGaoXuYang'

import xlwt
import re
import urllib2
import Queue
from bs4 import BeautifulSoup

# 设定源链接
url_origin = 'http://news.baidu.com'

"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%--函数--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"""
# 用来处理gbk报错的函数，去除非法的全角字符
def replace_character(string_get):
    string_get = string_get.replace(u'\xa0', u' ')
    string_get = string_get.replace(u'\xa4', u' ')
    string_get = string_get.replace(u'\x57', u' ')
    string_get = string_get.replace(u'\xa3', u' ')
    return string_get

"""
    get_news
    函数功能: 获取各个新闻的div
    url_soup 整个页面的soup
    news_type 新闻div的class
"""
def get_news(url_soup, news_type):
    news = url_soup.find_all(attrs=news_type)
    return news

"""
    get_title
    函数功能: 获取标题的文本
    news_list_all 新闻div的list
    title_type 标题div的class
"""
def get_title(news_list_all, title_type):
    title_list_all = range(len(news_list_all))
    combo = 0
    for a in news_list_all:
        title_list_all[combo] = news_list_all[combo].find(attrs=title_type)
        title_list_all[combo] = title_list_all[combo].get_text()
        combo += 1
    return title_list_all

"""
    get_author
    函数功能: 获取来源和时间的文本
    news_list_all 新闻div的list
    author_type 来源和时间div的class
"""
def get_author(news_list_all, author_type):
    author_list_all = range(len(news_list_all))
    combo = 0
    for b in news_list_all:
        author_list_all[combo] = news_list_all[combo].find(attrs=author_type)
        author_list_all[combo] = author_list_all[combo].get_text()
        combo += 1
    combo = 0
    # 标题和时间的内容中会有不规则字符，应根据具体情况扩充或注释掉
    for c in author_list_all:
        author_list_all[combo] = replace_character(c)
        combo += 1
    return author_list_all

"""
    get_abstract
    函数功能: 获取摘要，太费资源故不使用
"""
def get_abstract(news_list_all, abstract_type):
    abstract_list_all = range(len(news_list_all))
    combo = 0
    for d in news_list_all:
        abstract_list_all[combo] = news_list_all[combo].find(attrs=abstract_type)
        abstract_list_all[combo] = abstract_list_all[combo].get_text()
        combo += 1
    combo = 0
    for e in abstract_list_all:
        abstract_list_all[combo] = replace_character(e)
        combo += 1
    return abstract_list_all

"""
    get_href
    函数功能: 获取标题链接
    news_list_all 新闻div的list
"""
def get_href(news_list_all):
    href_list_all = range(len(news_list_all))
    combo = 0
    for f in news_list_all:
        href_list_all[combo] = news_list_all[combo].a
        href_list_all[combo] = href_list_all[combo].get('href')
        combo += 1
    return href_list_all

"""
    get_next
    函数功能: 获取下一页链接
    url_soup 整个页面的soup
    flip_type 下一页div的class
"""
def get_next(url_soup, flip_type):
    flip_list = url_soup.find_all(attrs=flip_type)
    try:
        url_next = flip_list[1]
    except:
        return None
    f = flip_list[1].get_text()
    if re.search(u"下一页", f) != None:
        return url_origin + url_next.get('href')
    return None



"""
    cut_source_time
    函数功能: 将author切分为新闻来源和年月
    author_origin author的list
"""
def cut_source_time(author_origin):
    source = range(len(author_origin))
    time_year = range(len(author_origin))
    time_month = range(len(author_origin))
    combo = 0
    for element in author_origin:
        trans = element.split('2')
        trans2 = re.findall(r'(\w*[0-9]+)\w*', element)
        source[combo] = trans[0].strip()
        time_year[combo] = trans2[0]
        time_month[combo] = trans2[1]
        combo += 1
    return source, time_year, time_month
"""%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%--结束--%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"""


if __name__ == "__main__":
    # 创建excel，仅是为了处理数据
    My_Text = xlwt.Workbook(encoding='GB2312')
    worksheet = My_Text.add_sheet('My_Sheet')

    # 打开结果保存的文件，测试时可以使用.txt格式，若用js读取的话应使用xml或者json
    # file_json_result = open('file_json_result.json', 'w')

    # 创建FIFO
    url_list = Queue.Queue()

    # 存入起始链接
    url_list.put('http://news.baidu.com/ns?word=%E7%94%B5%E5%AD%90%E7%A7%91%E6%8A%80%E5%A4%A7%E5%AD%A6&pn=20&cl=2&ct=0&tn=news&rn=20&ie=utf-8&bt=0&et=0')
    flag = True
    page = 0
    # 从第二页开始读取
    while((flag != None) and (page <=74000)):
        # 从队列中读取起始链接(链接读取之后会删除以节省空间)
        url_content = urllib2.urlopen(url_list.get()).read()

        # 使用soup解析当前网页
        soup = BeautifulSoup(url_content, "lxml")

        # 这一页所有的新闻列表(20条或者更少)
        news_list = get_news(soup, {"class": "result"})
        # 获取所有新闻的标题列表
        title_list = get_title(news_list, {"class": "c-title"})
        # 获取标题的href
        href_list = get_href(news_list)
        # 获取所有新闻的来源和发布时间
        author_list = get_author(news_list, {"class": "c-author"})
        # 获取下一页的url
        flip_next = get_next(soup, {"class": "n"})

        soure_list, time_year_list, time_month_list = cut_source_time(author_list)
        max_list = 0
        for a in title_list:
            worksheet.write(page, 0, title_list[max_list])
            worksheet.write(page, 1, soure_list[max_list])
            worksheet.write(page, 2, href_list[max_list])
            worksheet.write(page, 3, time_year_list[max_list] + "." + time_month_list[max_list])
            worksheet.write(page, 4, time_year_list[max_list])
            worksheet.write(page, 5, time_month_list[max_list])
            page += 1
            max_list += 1

        if flip_next == None:
            flag = None
        else:
            url_list.put(flip_next)
            flag = True
        print page

    # 关闭表格
    My_Text.save('My.xls')
    # 关闭文件
    # file_json_result.close()

