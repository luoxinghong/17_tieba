# -*- coding: utf-8 -*-
BOT_NAME = 'tieba_tzy'
SPIDER_MODULES = ['tieba_tzy.spiders']
NEWSPIDER_MODULE = 'tieba_tzy.spiders'
ROBOTSTXT_OBEY = False


ITEM_PIPELINES = {
   'tieba_tzy.pipelines.TiebaTzyPipeline': 300,
}

# TODO
# MYSQL_HOST = '106.12.8.109'
MYSQL_HOST = 'localhost'
MYSQL_USER = 'root'
MYSQL_PASSWD = 'lxh123'
MYSQL_PORT = 3306

# TODO
LOG_FILE = "test.log"
LOG_LEVEL = "INFO"


# SPIDER_MIDDLEWARES = {
#    'tieba_tzy.middlewares.TiebaTzySpiderMiddleware': 543,
# }

DOWNLOADER_MIDDLEWARES = {
   'tieba_tzy.middlewares.TiebaTzyDownloaderMiddleware': 543,
   # 'tieba_tzy.middlewares.ABProxyMiddleware': 1,
   # 'tieba_tzy.middlewares.RandomUserAgentMiddleware': 2,
   # 'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
}

# 配置user_agent的随机类型
RANDOM_UA_TYPE = 'random'

# 增加爬虫速度及防ban配置
# DOWNLOAD_DELAY = 0
# DOWNLOAD_FAIL_ON_DATALOSS = False
# CONCURRENT_REQUESTS = 5
# CONCURRENT_REQUESTS_PER_DOMAIN = 5
# CONCURRENT_REQUESTS_PER_IP = 5
# COOKIES_ENABLED = False
# DOWNLOAD_TIMEOUT = 60

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 0.2  # 初始下载延迟
DOWNLOAD_DELAY = 0.2  # 每次请求间隔时间