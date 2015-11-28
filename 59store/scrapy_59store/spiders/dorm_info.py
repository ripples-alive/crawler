# -*- coding: utf-8 -*-
import json

import scrapy
from scrapy_59store.items import DormInfoItem


class DormInfoSpider(scrapy.Spider):
    name = "dorm_info"
    allowed_domains = ["yemao.59store.com"]
    start_urls = (
        'http://yemao.59store.com/entry/getAllProvinceList',
    )
    handle_httpstatus_list = [302]

    def parse(self, response):
        item = DormInfoItem()
        provinceList = json.loads(response.body)['data']
        for province in provinceList:
            item['province'] = province['name']
            meta = {'dont_redirect': True, 'item': item.copy()}
            path = '/entry/getAllCityListByProvinceId'
            path += '?provinceId={0}'.format(province['province_id'])
            yield scrapy.Request(response.urljoin(path), self.parse_city, meta=meta)

    def parse_city(self, response):
        item = response.meta['item']
        cityList = json.loads(response.body)['data']
        cityList = cityList[:1]
        for city in cityList:
            item['city'] = city['name']
            meta = {'dont_redirect': True, 'item': item.copy()}
            path = '/entry/getAllByCityId/cityId/{0}'.format(city['city_id'])
            yield scrapy.Request(response.urljoin(path), self.parse_site, meta=meta)

    def parse_site(self, response):
        item = response.meta['item']
        zoneList = json.loads(response.body)['data']
        zoneList = zoneList[:1]
        for zone in zoneList:
            siteList = zone['siteList']
            # In fact, this list should be dict.
            # However, because of JSON format, python sometimes decode it as list.
            if type(siteList) == dict:
                siteList = siteList.values()
            for site in siteList:
                item['school'] = site['site_name']
                meta = {'item': item.copy()}
                path = '/entry/index/site_id/{0}'.format(site['site_id'])
                # Must set dont_filter to False as all requests will be
                # redirected to the same url.
                yield scrapy.Request(response.urljoin(path), self.parse_dorm_entry_page, meta=meta, dont_filter=True)

    def parse_dorm_entry_page(self, response):
        meta = {'dont_redirect': True, 'item': response.meta['item']}
        path = '/dorm/getDormEntryListPC'
        yield scrapy.Request(response.urljoin(path), self.parse_dorm_entry, meta=meta, dont_filter=True)

    def parse_dorm_entry(self, response):
        item = response.meta['item']
        data = json.loads(response.body)['data']
        if not data:
            return
        groupList = data['groups']
        for group in groupList:
            for entry in group['entries']:
                item['dormentry'] = entry['dormentry_name']
                meta = {'dont_redirect': True, 'item': item.copy()}
                for dormentry in entry['dormentry']:
                    path = '/dorm/{0}'.format(dormentry['dormentry_id'])
                    yield scrapy.Request(response.urljoin(path), self.parse_dorm_page, meta=meta)

    def parse_dorm_page(self, response):
        meta = {'dont_redirect': True, 'item': response.meta['item']}
        path = '/dorm/getDormInfo'
        forms = {'dormentry_id': response.url.split('/')[-1]}
        yield scrapy.FormRequest(response.urljoin(path), self.parse_dorm, formdata=forms, meta=meta, dont_filter=True)

    def parse_dorm(self, response):
        item = DormInfoItem(response.meta['item'])
        dorm = json.loads(response.body)['data']
        item['notice'] = dorm['notice']
        item['floor'] = dorm['address3']
        item['latitude'] = dorm['longitude']
        item['longitude'] = dorm['longitude']
        item['student_number'] = dorm['student_number']
        yield item
