# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class DormInfoItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    province = scrapy.Field()
    city = scrapy.Field()
    school = scrapy.Field()
    dormentry = scrapy.Field()
    notice = scrapy.Field()
    floor = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    student_number = scrapy.Field()


class PrintDormItem(scrapy.Item):
    province = scrapy.Field()
    city = scrapy.Field()
    zone = scrapy.Field()
    school = scrapy.Field()
    region = scrapy.Field()
    dormentry = scrapy.Field()
    shop = scrapy.Field()
    shop_id = scrapy.Field()
    shop_status = scrapy.Field()
    business_status = scrapy.Field()
