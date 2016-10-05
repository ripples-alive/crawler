# -*- coding: utf-8 -*-
import json

import scrapy

from scrapy_59store.items import PrintDormItem


class PrintDormSpider(scrapy.Spider):
    name = "print_shop"
    allowed_domains = ["print.59store.com"]
    start_urls = (
        'http://print.59store.com/printapi/common/provinceList',
    )

    def parse(self, response):
        item = PrintDormItem()
        province_list = json.loads(response.body)['data']['contents']
        for province in province_list:
            item['province'] = province['value']
            path = '/printapi/common/cityList'
            path += '?provinceId={0}'.format(province['key'])
            yield scrapy.Request(response.urljoin(path), self.parse_city, meta={'item': item.copy()})

    def parse_city(self, response):
        item = response.meta['item']
        city_list = json.loads(response.body)['data']['contents']
        for city in city_list:
            item['city'] = city['value']
            path = '/printapi/common/zoneList'
            path += '?cityId={0}'.format(city['key'])
            yield scrapy.Request(response.urljoin(path), self.parse_zone, meta={'item': item.copy()})

    def parse_zone(self, response):
        item = response.meta['item']
        zone_list = json.loads(response.body)['data']['contents']
        for zone in zone_list:
            item['zone'] = zone['value']
            path = '/printapi/common/siteList'
            path += '?zoneId={0}'.format(zone['key'])
            yield scrapy.Request(response.urljoin(path), self.parse_school, meta={'item': item.copy()})

    def parse_school(self, response):
        item = response.meta['item']
        school_list = json.loads(response.body)['data']['contents']
        for school in school_list:
            item['school'] = school['value']
            path = '/printapi/common/dormShops'
            path += '?siteId={0}'.format(school['key'])
            yield scrapy.Request(response.urljoin(path), self.parse_dorm, meta={'item': item.copy()})

    def parse_dorm(self, response):
        item = response.meta['item']
        region_list = json.loads(response.body)['data']
        for region in region_list:
            item['region'] = region
            dorm_list = region_list[region]
            for dorm in dorm_list:
                item['dormentry'] = dorm['dormentryName']
                path = '/printapi/common/dormentrysShop'
                path += '?dormentryId={0}'.format(dorm['dormentryId'])
                yield scrapy.Request(response.urljoin(path), self.parse_shop, meta={'item': item.copy()})

    def parse_shop(self, response):
        item = response.meta['item']
        data = json.loads(response.body)['data']
        if not data:
            yield item.copy()
            return
        shop_list = data['shopInfos']
        for shop in shop_list:
            item['shop'] = shop['shopName']
            item['shop_id'] = shop['shopId']
            item['shop_status'] = shop['shopStatus']
            item['business_status'] = shop['businessStatus']
            yield item.copy()
