# -*- coding: utf-8 -*-

# Scrapy settings for duxiu project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'duxiu'

SPIDER_MODULES = ['duxiu.spiders']
NEWSPIDER_MODULE = 'duxiu.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'duxiu (+http://www.yourdomain.com)'

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS=32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY=3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN=16
#CONCURRENT_REQUESTS_PER_IP=16

# Disable cookies (enabled by default)
COOKIES_ENABLED=False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED=False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Cookie': 'JSESSIONID=9F1D7BBB6CC2F4432712D87E5F2B84AE.tomcat217; duxiu=userName%5fdsr%2c%3dshr%2c%21userid%5fdsr%2c%3d10321%2c%21char%5fdsr%2c%3d%2c%21metaType%2c%3d0%2c%21dsr%5ffrom%2c%3d1%2c%21logo%5fdsr%2c%3dunits%5flogo%2flogo%5fexp%2ejpg%2c%21logosmall%5fdsr%2c%3dunits%5flogo%2flogosmall%5fexp%2ejpg%2c%21title%5fdsr%2c%3d%u8bfb%u79c0%u4f53%u9a8c%u7248%2c%21url%5fdsr%2c%3d%2c%21compcode%5fdsr%2c%3d%2c%21province%5fdsr%2c%3d%u5176%u5b83%2c%21readDom%2c%3d0%2c%21isdomain%2c%3d3%2c%21showcol%2c%3d0%2c%21hu%2c%3d0%2c%21areaid%2c%3d0%2c%21uscol%2c%3d0%2c%21isfirst%2c%3d2%2c%21istest%2c%3d1%2c%21cdb%2c%3d0%2c%21og%2c%3d0%2c%21testornot%2c%3d0%2c%21remind%2c%3d0%2c%21datecount%2c%3d4878%2c%21userIPType%2c%3d1%2c%21lt%2c%3d1%2c%21ttt%2c%3dduxiu%2c%21enc%5fdsr%2c%3d672593FD4F2F58A69ADD9C8996746E47; AID_dsr=3946; superlib=""; msign_dsr=1472014225919; DSSTASH_LOG=C%5f1%2dUN%5f3946%2dUS%5f0%2dT%5f1472014225936; bdshare_firstime=1472014255789; fresh_dsr=1472016423927; CNZZDATA2088844=cnzz_eid%3D1566356972-1472012614-http%253A%252F%252Fwww.duxiu.com%252F%26ntime%3D1472012614',
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'duxiu.middlewares.MyCustomSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'duxiu.middlewares.MyCustomDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'duxiu.pipelines.SomePipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# NOTE: AutoThrottle will honour the standard settings for concurrency and delay
AUTOTHROTTLE_ENABLED=True
# The initial download delay
#AUTOTHROTTLE_START_DELAY=5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY=60
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG=False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED=True
#HTTPCACHE_EXPIRATION_SECS=0
#HTTPCACHE_DIR='httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES=[]
#HTTPCACHE_STORAGE='scrapy.extensions.httpcache.FilesystemCacheStorage'
