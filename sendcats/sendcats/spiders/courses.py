# -*- coding: utf-8 -*-
import json
import urllib
import urlparse

import scrapy
import logging


class CoursesSpider(scrapy.Spider):
    name = "courses"
    allowed_domains = ["www.sendcats.com"]
    start_urls = (
        'http://www.sendcats.com/resource/list?is_211=0&is_985=0&page=1',
        'http://www.sendcats.com/resource/list?is_211=0&is_985=1&page=1',
        'http://www.sendcats.com/resource/list?is_211=1&is_985=0&page=1',
        'http://www.sendcats.com/resource/list?is_211=1&is_985=1&page=1',
    )

    def parse(self, response):
        data = json.loads(response.body)
        if data['err'] != 0:
            logging.warning('failed request: {}'.format(response.url))
            return
        school_list = data['resource_list']
        if not school_list:
            return
        yield scrapy.Request(self.get_next_url(response.url), self.parse)
        for school in school_list:
            url = u'http://www.sendcats.com/resource/university?university={}'
            url = url.format(school['university'])
            yield scrapy.Request(url, self.parse_college, meta={'school': school['university']})

    def parse_college(self, response):
        school = response.meta['school']
        data = json.loads(response.body)
        if data['err'] != 0:
            logging.warning('failed request: {}'.format(response.url))
            return
        college_list = data['college_resource_num']
        for college in college_list:
            url = u'http://www.sendcats.com/resource/college?college={}&university={}&page=1'
            url = url.format(college['college'], school)
            yield scrapy.Request(url, self.parse_course)

    def parse_course(self, response):
        data = json.loads(response.body)
        if data['err'] != 0:
            logging.warning('failed request: {}'.format(response.url))
            return
        course_list = data['course_list']
        if not course_list:
            return
        yield scrapy.Request(self.get_next_url(response.url), self.parse_course)
        for course in course_list:
            yield course

    def get_next_url(self, url):
        parsed_url = urlparse.urlparse(url)
        parsed_query = urlparse.parse_qs(parsed_url.query)
        parsed_query['page'][0] = int(parsed_query['page'][0]) + 1
        parsed_url = list(parsed_url)
        # query is the forth element
        parsed_url[4] = urllib.urlencode(parsed_query, True)
        return urlparse.urlunparse(parsed_url)
