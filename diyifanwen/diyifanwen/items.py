# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DocumentItem(scrapy.Item):
    title = scrapy.Field()
    download_url = scrapy.Field()
    post_url = scrapy.Field()
    directory = scrapy.Field()
