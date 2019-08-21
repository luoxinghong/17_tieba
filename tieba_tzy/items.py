# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class commentItem(scrapy.Item):
    # define the fields for your item here like:
    post_id = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    comment_time = scrapy.Field()
    comment_id = scrapy.Field()
    tieba_name = scrapy.Field()

class postItem(scrapy.Item):
    # define the fields for your item here like:
    post_id = scrapy.Field()
    author = scrapy.Field()
    content = scrapy.Field()
    thread_title = scrapy.Field()
    thread_id = scrapy.Field()
    floor = scrapy.Field()
    comment_num = scrapy.Field()
    tieba_name = scrapy.Field()

class threadItem(scrapy.Item):
    # define the fields for your item here like:
    thread_author = scrapy.Field()
    thread_title = scrapy.Field()
    thread_id = scrapy.Field()
    tieba_name = scrapy.Field()




