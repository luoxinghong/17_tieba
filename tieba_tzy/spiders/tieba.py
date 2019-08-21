# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
import json
from ..items import commentItem, postItem, threadItem
import emoji
import re
from lxml import etree
import requests
from xpinyin import Pinyin
import MySQLdb


def filter_emoji(desstr, restr=''):
    # 过滤表情
    try:
        co = re.compile(u'[\U00010000-\U0010ffff]')
    except re.error:
        co = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
    return co.sub(restr, desstr)


class TiebaSpider(scrapy.Spider):
    name = 'tieba'
    pin = Pinyin()

    # tieba = ['王俊凯', '刘德华', '周杰伦', "杨幂", "沙溢", "韩寒", "朴树", "王菲"]
    tieba = ["刘德华"]

    # 转成拼音
    tieba_py = []
    for _ in tieba:
        tieba_py.append(pin.get_pinyin(_).replace("-", ''))

    base_url = 'https://tieba.baidu.com/f?kw=%s&ie=utf-8&pn=%s'

    page_list = []

    # 获取每个贴吧的页数
    for tieba_name in tieba:
        html = requests.get(base_url % (tieba_name, 0)).content.decode('utf-8')
        dom_tree = etree.HTML(html)
        page_str = dom_tree.xpath("//*[@id='frs_list_pager']/a[contains(@class,'last')]/@href")[0]

        # 获取总页数
        page = re.search(r'(?<=pn=).+', page_str).group(0)

        # 每50页于网页中是同一个网页
        page = 1 + int(page) // 50
        page_list.append(page)

    assert len(tieba) == len(tieba_py)
    assert len(tieba) == len(page_list)

    db = MySQLdb.connect("localhost", 'root', 'lxh123', charset='utf8')
    create_table1 = '''CREATE TABLE `comment` (   `content` varchar(5000) CHARACTER SET utf8mb4 NOT NULL,   `author` varchar(500) NOT NULL,   `post_id` varchar(5000) NOT NULL,   `comment_time` datetime(6) NOT NULL,   `comment_id` varchar(5000) NOT NULL ) ENGINE=InnoDB DEFAULT CHARSET=utf8;'''
    create_table2 = '''CREATE TABLE `thread` (   `thread_id` varchar(5000) NOT NULL,   `thread_title` varchar(5000) NOT NULL,   `thread_author` varchar(5000) NOT NULL ) ENGINE=InnoDB DEFAULT CHARSET=utf8;'''
    create_table3 = '''CREATE TABLE `post` (   `post_id` varchar(5000) NOT NULL,   `author` varchar(500) NOT NULL,   `content` varchar(5000) NOT NULL,   `thread_id` varchar(5000) NOT NULL,   `comment_num` varchar(500) NOT NULL,   `floor` varchar(5000) NOT NULL ) ENGINE=InnoDB DEFAULT CHARSET=utf8;'''
    cursor = db.cursor()

    # 若sql中不存在某贴吧则创建
    for _ in tieba_py:
        res = cursor.execute("SHOW DATABASES LIKE '%s';" % (_))

        if res == 0:
            res = cursor.execute('''CREATE DATABASE IF NOT EXISTS %s;''' % (_))
            res = cursor.execute('''use %s;''' % (_))
            res = cursor.execute(create_table1)

            res = cursor.execute(create_table2)
            res = cursor.execute(create_table3)

    cursor.close()
    db.close()

    def start_requests(self):
        # 遍历所有贴吧所有页数
        for l in range(len(self.page_list)):
            for i in range(self.page_list[l]):
                # print(self.tieba_py[l], i + 1)
                url = self.base_url % (self.tieba[l], i * 50)
                yield Request(url, callback=self.parse, meta={'tieba_name': self.tieba_py[l]})

    # 处理贴吧页
    def parse(self, response):
        try:
            tieba_name = response.meta['tieba_name']
        except Exception as e:
            print(e)
        thread_replys = response.xpath(
            "//li[contains(@class,'j_thread_list')]/div/div/span[contains(@title,'回复')]").xpath('string(.)').extract()
        thread_ids = response.xpath(
            "//li[contains(@class,'j_thread_list')]/div/div/div/div/a[contains(@href,'/p/')]/@href").extract()
        thread_titles = response.xpath("//li[contains(@class,'j_thread_list')]/div/div/div/div/a/@title").extract()
        thread_authors = response.xpath(
            "//li[contains(@class,'j_thread_list')]/div/div/div/div/span[contains(@title,'主题作者')]").xpath(
            'string(.)').extract()

        assert len(thread_ids) == len(thread_titles)
        assert len(thread_authors) == len(thread_titles)
        assert len(thread_replys) == len(thread_ids)

        for i in range(len(thread_ids)):
            thread_reply = thread_replys[i]
            thread_id = thread_ids[i]
            if int(thread_reply) < 3:
                continue
            if not thread_id.startswith('/p'):
                continue
            thread_title = thread_titles[i]
            thread_author = thread_authors[i]
            yield Request('https://tieba.baidu.com' + thread_id,
                          self.parse_thread,
                          meta={'tieba_name': tieba_name, 'thread_id': thread_id[3:], 'thread_title': thread_title,
                                'thread_author': thread_author})

    # 处理贴子页
    def parse_thread(self, response):
        tieba_name = response.meta['tieba_name']
        tItem = threadItem()
        # thread_title = response.xpath("//*[@id='j_core_title_wrap']/h3").xpath('string(.)').extract_first()
        thread_title = response.meta['thread_title']
        thread_title = filter_emoji(thread_title)
        tItem['thread_title'] = thread_title
        tItem['thread_author'] = response.meta['thread_author']
        tItem['thread_id'] = response.meta['thread_id']
        tItem['tieba_name'] = tieba_name
        print(tItem)
        print("*"*100)
        yield tItem

        all_dict = response.xpath("//div[contains(@class, 'l_post')]/@data-field").extract()
        for dict_str in all_dict:
            dict = json.loads(dict_str)

            item = postItem()
            item['thread_id'] = response.meta['thread_id']
            item['author'] = dict['author']['user_name']
            item['floor'] = dict['content']['post_no']
            item['post_id'] = dict['content']['post_id']
            item['comment_num'] = dict['content']['comment_num']
            item['tieba_name'] = tieba_name

            content = response.xpath("//*[@id='post_content_%s']/text()" % item['post_id']).extract()

            content = '。'.join(content)
            content = content.strip().replace('\n', '。')
            content = filter_emoji(content)
            if len(content) > 200:
                content = ''
            item['content'] = content

            yield item
            comment_num = item['comment_num']
            if comment_num > 0:
                pn = comment_num // 10
                for i in range(pn + 1):
                    url = 'https://tieba.baidu.com/p/comment?tid={}&pid={}&pn={}'.format(item['thread_id'],
                                                                                         item['post_id'], i + 1)
                    # url = 'https://tieba.baidu.com/p/comment?tid=4560773990&pid=90094895254&pn=1'.format(item['thread_id'],item['post_id'],i+1)
                    yield Request(url, self.parse_post,
                                  meta={'tieba_name': tieba_name, 'post_id': item['post_id'], 'page': i})

        next_page = response.xpath(".//ul[@class='l_posts_num']//a[text()='下一页']/@href").extract_first()
        if next_page:
            yield Request('http://tieba.baidu.com' + next_page, meta={'tieba_name': tieba_name})

    # 处理某层楼
    def parse_post(self, response):
        tieba_name = response.meta['tieba_name']

        # return
        all_authors = response.xpath("/html/body/li[contains(@class,'lzl_single_post')]/div/a").xpath(
            'string(.)').extract()
        all_contents = response.xpath("/html/body/li[contains(@class,'lzl_single_post')]/div/span").xpath(
            'string(.)').extract()
        # all_times = response.xpath("/html/body/li[contains(@class,'lzl_single_post')]/div/div/span[3]").xpath('string(.)').extract()
        all_times = response.xpath(
            "/html/body/li[contains(@class,'lzl_single_post')]/div/div/span[contains(@class,'lzl_time')]").xpath(
            'string(.)').extract()
        assert len(all_authors) == len(all_contents)
        assert len(all_authors) == len(all_times)

        for i in range(len(all_authors)):
            item = commentItem()

            item['author'] = all_authors[i]
            item['post_id'] = response.meta['post_id']
            item['comment_id'] = (i + 1) + 10 * response.meta['page']
            item['comment_time'] = all_times[i]
            item['tieba_name'] = tieba_name
            comment = all_contents[i].strip().replace('\n', '。').replace('\r\n', '。')
            item['content'] = filter_emoji(comment)
            yield item
