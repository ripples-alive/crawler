# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ShopItem(scrapy.Item):
    # define the fields for your item here like:
    shop_id = scrapy.Field()
    cellphone = scrapy.Field()
    gender = scrapy.Field()
    name = scrapy.Field()
    alias_name = scrapy.Field()
    school = scrapy.Field()
    build = scrapy.Field()
