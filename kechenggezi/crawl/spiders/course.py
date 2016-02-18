# -*- coding: utf-8 -*-
import md5
import json
import time
import string
import random

import scrapy
import logging
from crawl.items import CourseItem


class CourseSpider(scrapy.Spider):
    name = "course"
    allowed_domains = ["kechenggezi.com"]
    start_urls = (
        'http://www.kechenggezi.com/',
    )

    def parse(self, response):
        data = {
            "user": {
                "gezi_id": 0,
                "grade": 2015,
                "common_friends_count": 0,
                "is_officer": False,
                "android_imei": "02B77C17C11F1DA9D5217B7E3CBE250F9C",
                "sex": 0,
                "pursuing_degree": "大学生",
                "friends_count": 0,
                "name": "default_name",
                "common_courses_count": 0,
                "friend_relationship": 0,
                "renren_id": 0,
                "has_avatar": False,
                "birthday_visibility": 0,
                "is_moderator": False,
                "is_verified": False,
                "signup_from": 1,
                "courses_count": 0
            },
            "screen_width": 720,
            "school_name": "",
            "renren_id": 0,
            "version": "7.2.0",
            "department_name": "",
            "screen_height": 1440
        }
        url = 'http://kechenggezi.com/mobile/pre_register.json?version=7.2.0&device_type=android&request_time=1.455600708809E9'
        school_list = open('schools').read().strip().split('\n')
        for school in school_list:
            tmp = '1' + md5.new(str(random.random())).hexdigest().upper()
            data['user']['android_imei'] = tmp + md5.new(tmp).hexdigest()[0].upper()
            data['school_name'] = school
            yield scrapy.Request(url, self.parse_registered, 'POST',
                {'Content-Type': 'application/json'}, json.dumps(data),
                meta={'school': school}, dont_filter=True)

    def parse_registered(self, response):
        try:
            token = json.loads(response.body)['kecheng_token']
        except Exception as e:
            logging.warning('{}: {}'.format(response.meta['school'], response.body))
            return
        url = 'http://kechenggezi.com/search.json?term=&token={}&version=7.2.1&device_type=android&request_time=1.455370762539E9'
        yield scrapy.Request(url.format(token), self.parse_courses,
            meta={'school': response.meta['school'], 'token': token})

    def parse_courses(self, response):
        yield CourseItem(token=response.meta['token'],
            school=response.meta['school'], response=response.body)
