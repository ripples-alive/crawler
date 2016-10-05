# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class PaperItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    main_class = scrapy.Field()
    sub_class = scrapy.Field()
    post_url = scrapy.Field()
