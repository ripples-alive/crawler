# -*- coding: utf-8 -*-

import re

import scrapy

from it168.items import DocumentItem


class DocumentSpider(scrapy.Spider):
    name = "document"
    allowed_domains = ["wenku.it168.com"]
    start_urls = (
        'http://wenku.it168.com/list/',
    )

    def parse(self, response):
        next_url = response.xpath(
            u'//div[@class="page1"]/a[text()="[下一页]"]/@href').extract_first()
        if next_url is None:
            return
        yield scrapy.Request(response.urljoin(next_url), self.parse)

        for url in response.xpath('//div[@class="cont7"]/div/a[@title]/@href').extract():
            yield scrapy.Request(response.urljoin(url), self.parse_post)

    def parse_post(self, response):
        title = response.xpath(
            '//div[@class="bor13"]/div/h1/a/text()').extract_first()
        if title is None:
            title = response.xpath(
                '//div[@class="tit28"]/a/text()').extract_first()
        if title is None:
            title = re.search('<h1>.*title="(.*)".*</h1>',
                              response.body.replace('\n', '')).group(1)
        title = title.strip()
        classification = response.xpath(
            '//div[@class="posi_1202"]/a[position()>1]/text()').extract()
        description = response.xpath(
            '//div[@class="l"]/ul/li[1]/text()').extract_first()
        coin = re.search(u'所需金币：(\d+)', description).group(1)
        size = re.search(u'大小：([^B]+B)', description).group(1)
        tags = response.xpath('//div[@class="docTagsLink"]/a/text()').extract()
        tags = map(lambda x: x.strip(), tags)
        yield DocumentItem(title=title, classification=classification,
                           post_url=response.url, size=size, coin=coin, tags=tags)
