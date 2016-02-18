# -*- coding: utf-8 -*-
import json
import re

import scrapy
import logging
from quweikaochang.items import QuweikaochangItem


class ExaminationSpider(scrapy.Spider):
    name = "examination"
    allowed_domains = ["k.thea.cn"]

    def start_requests(self):
        return [scrapy.FormRequest('http://k.thea.cn/index.php?c=login&a=log',
            self.parse,
            formdata={'username': raw_input('username: '), 'from': 'k_index', 'password': raw_input('password: ')})]

    def parse(self, response):
        for url in response.xpath('//*[@src]/@src').extract():
            yield scrapy.Request(url, self.parse_start)

    def parse_start(self, response):
        yield scrapy.Request('http://k.thea.cn/index.php', self.parse_categories)

    def parse_categories(self, response):
        categories_path = "//div[@class='p_wrap']//a[contains(@href, 'c=exam')]/@href"
        for path in response.xpath(categories_path).extract():
            path += '&a=visitorVip'
            yield scrapy.Request(response.urljoin(path), self.parse_list)

    def parse_list(self, response):
        next_path = '//*[@id="page"]//a[contains(@class, "next")]/@href'
        next_page = response.xpath(next_path).extract_first()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page), self.parse_list)

        paper_id_pattern = re.compile('papersid=(\d+)')
        details_path = '//*[@id="paperslist"]/dd//a[contains(@href, "a=papersInfo")]'
        for detail_dom in response.xpath(details_path):
            title = detail_dom.xpath('text()').extract_first()
            path = detail_dom.xpath('@href').extract_first()
            paper_id = int(paper_id_pattern.search(path).group(1))
            url = 'http://k.thea.cn/index.php?c=exam&a=downloadPermissionVip&papersid={}'.format(paper_id)
            # url = 'http://k.thea.cn/index.php?c=exam&a=downloadPermission&papersid={}'.format(paper_id)
            yield scrapy.Request(url, self.parse_permission,
                meta={'title': title, 'paper_id': paper_id})

    def parse_permission(self, response):
        title = response.meta['title']
        paper_id = response.meta['paper_id']
        res_obj = json.loads(response.body)
        if res_obj['error'] != '0':
            self.log('get permission error: ' + response.body)
            return

        url = 'http://k.thea.cn/index.php?c=exam&a=download&papersid={}&downloadCode={}'.format(paper_id, res_obj['downloadCode'])
        yield QuweikaochangItem(title=title, msg=res_obj['msg'], url=url)
