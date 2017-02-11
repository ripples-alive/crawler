# -*- coding: utf-8 -*-

import md5
import time
import json
import urllib

import scrapy
from scrapy.shell import inspect_response

from anlaiye.items import ShopItem


class ShopSpider(scrapy.Spider):
    name = "shop"
    allowed_domains = ["anlaiye.com.cn"]

    def start_requests(self):
        return [
            scrapy.FormRequest('https://pub-v2.anlaiye.com.cn/api/school/citylist',
                formdata=self.gen_form({}), callback=self.parse)
        ]

    def parse(self, response):
        url ='https://pub-v2.anlaiye.com.cn/api/school/schoollist'
        res_data = json.loads(response.body)
        city_list = res_data['data']['opening']
        for city in city_list:
            form = self.gen_form({'city_id': city['city_id']})
            yield scrapy.FormRequest(url, self.parse_school, formdata=form)

    def parse_school(self, response):
        item = ShopItem()
        url ='https://pub-v2.anlaiye.com.cn/api/build/dorms'
        res_data = json.loads(response.body)
        distinct_list = res_data['data']['opening']
        for distinct in distinct_list:
            school_list = distinct['child_list']
            for school in school_list:
                item['school'] = school['school_name']
                form = self.gen_form({'school_id': school['school_id']})
                yield scrapy.FormRequest(url, self.parse_dorm, formdata=form, meta={'item': item.copy()})

    def parse_dorm(self, response):
        item = response.meta['item']
        url ='https://passport-v2.anlaiye.com.cn/api/userinfo/getMastersOfBuild'
        res_data = json.loads(response.body)
        build_list = res_data['data']
        for build in build_list:
            item['build'] = build['build_name']
            form = self.gen_form({'build_id': build['build_id']})
            yield scrapy.FormRequest(url, self.parse_floor, formdata=form, meta={'item': item.copy()})

    def parse_floor(self, response):
        item = response.meta['item']
        url ='https://passport-v2.anlaiye.com.cn/api/earth/getinfoForUser'
        res_data = json.loads(response.body)
        floor_list = res_data['data']
        # in fact we could stop iteration if we only need cellphone
        for floor in floor_list:
            if floor['user_id'] != 0:
                form = self.gen_form({'earth_uid': floor['user_id']})
                yield scrapy.FormRequest(url, self.parse_user, formdata=form, meta={'item': item.copy()})

    def parse_user(self, response):
        item = response.meta['item']
        res_data = json.loads(response.body)
        user = res_data['data']
        item['shop_id'] = user['user_id']
        item['cellphone'] = user['phone']
        item['gender'] = user['gender']
        item['name'] = user['addressee_name']
        item['alias_name'] = user['alias_name']
        yield item
        # yield ShopItem(
        #     shop_id=user['user_id'],
        #     phone=user['phone'],
        #     gender=user['gender']
        # )
        # user = res_data['data']
        # print json.dumps(res_data, indent=4)
        # inspect_response(response, self)
        # exit()

    def gen_form(self, data):
        data = json.dumps(data, separators=(',', ':'))
        data = urllib.quote(data)
        data = data.replace('+', '%20')
        params = {
            'app_version': '3.0.5',
            'client_type': '2',
            'data': data,
            'device_id': '863100037640582',
            'time': str(int(time.time())),
        }
        self.sign_params(params)
        return params

    def sign_params(self, params):
        sign = params['app_version']
        sign += '2'
        sign += params['data']
        sign += params['device_id']
        sign += params['time']
        sign += 'nK!op4w9lB.alev0'
        sign = md5.new(sign).hexdigest()
        params['sign'] = sign
