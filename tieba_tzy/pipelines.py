# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import MySQLdb
from .items import commentItem,postItem,threadItem
import traceback

class TiebaTzyPipeline(object):

    commentInsert = '''insert into comment(post_id,author,content,comment_time,comment_id) values("{post_id}","{author}","{content}","{comment_time}","{comment_id}")'''
    postInsert = '''insert into post(post_id,author,content,thread_id,comment_num,floor) values("{post_id}","{author}","{content}","{thread_id}","{comment_num}","{floor}")'''
    threadInsert = '''insert into thread(thread_author,thread_title,thread_id) values("{thread_author}","{thread_title}","{thread_id}")'''
    current_db = None
    def __init__(self, settings):
        self.settings = settings

    def process_item(self, item, spider):
        item_db = item['tieba_name']

        if self.current_db is None:
            self.cursor.execute('''use %s;'''%(item_db))
            self.current_db = item_db
        elif self.current_db != item_db:
            self.cursor.execute('''use %s;'''%(item_db))
            self.current_db = item_db



        if isinstance(item, commentItem):
            sqltext = self.commentInsert.format(
                post_id=int(item['post_id']),
                author=item['author'],
                content=pymysql.escape_string(item['content']),
                comment_time=item['comment_time'],
                comment_id=item['comment_id'])
            self.cursor.execute(sqltext)
        elif isinstance(item, postItem):
            sqltext = self.postInsert.format(
                post_id=int(item['post_id']),
                author=item['author'],
                content=pymysql.escape_string(item['content']),
                thread_id=int(item['thread_id']),
                comment_num=int(item['comment_num']),
                floor=int(item['floor']))
            self.cursor.execute(sqltext)
        elif isinstance(item, threadItem):
            sqltext = self.threadInsert.format(
                thread_author=item['thread_author'],
                thread_title=pymysql.escape_string(item['thread_title']),
                thread_id=int(item['thread_id']))
            self.cursor.execute(sqltext)
        return item


    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def open_spider(self, spider):

        self.connect = MySQLdb.connect(self.settings.get('MYSQL_HOST'), self.settings.get('MYSQL_USER'), self.settings.get('MYSQL_PASSWD'), charset='utf8')
        # 连接数据库
        # self.connect = pymysql.connect(
        #     host=self.settings.get('MYSQL_HOST'),
        #     port=self.settings.get('MYSQL_PORT'),
        #     db=self.settings.get('MYSQL_DBNAME'),
        #     user=self.settings.get('MYSQL_USER'),
        #     passwd=self.settings.get('MYSQL_PASSWD'),
        #     charset='utf8',
        #     use_unicode=True)

        # 通过cursor执行增删查改
        self.cursor = self.connect.cursor();
        self.connect.autocommit(True)

    def close_spider(self, spider):
        self.cursor.close()
        self.connect.close()

