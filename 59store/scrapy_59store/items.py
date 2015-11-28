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
