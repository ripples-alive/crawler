# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DocumentItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    classification = scrapy.Field()
    post_url = scrapy.Field()
    size = scrapy.Field()
    coin = scrapy.Field()
    tags = scrapy.Field()
