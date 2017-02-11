# -*- coding: utf-8 -*-
import os

import scrapy
from diyifanwen.items import DocumentItem


class DocumentSpider(scrapy.Spider):
    name = "document"
    allowed_domains = ["diyifanwen.com"]
    start_urls = [
        'http://www.diyifanwen.com/yanjianggao/',
        'http://www.diyifanwen.com/fanwen/biyelunwen/',
        'http://www.diyifanwen.com/qiuzhijiuzhi/jianliziliao/',
    ]

    def parse(self, response):
        index_main = response.xpath('//div[@id="IndexMain"]')
        if index_main:
            for url in index_main.xpath('//dl[@class="IndexDl"]/dt/a/@href').extract():
                yield scrapy.Request(response.urljoin(url), callback=self.parse)
            return

        list_main = response.xpath('//div[@id="ListMain"]')
        if list_main:
            for url in list_main.xpath('//a[@class="SLmore"]/@href').extract():
                yield scrapy.Request(response.urljoin(url), callback=self.parse)
            return

        art_main = response.xpath('//div[@id="ArtMain"]')
        if art_main:
            next_url = art_main.xpath(u'//*[@class="CnPage" and text()="下一页" and @href]/@href').extract_first()
            if next_url is not None:
                yield scrapy.Request(response.urljoin(next_url), callback=self.parse)
            for post_url in response.xpath('//div[@id="AListBox"]/ul/li/a/@href').extract():
                yield scrapy.Request(response.urljoin(post_url), callback=self.parse_post)
            return

    def parse_post(self, response):
        title = response.xpath('//div[@id="ArtContent"]/h1/text()').extract_first()
        directory = os.path.join(*response.xpath('//div[@id="Position"]//a/text()').extract()[1:])
        download_key = response.xpath('//input').re(r"DownFiles\('(.*)'\)")
        if download_key:
            download_url = ''.join([chr(int(x) - 799) for x in download_key[0].split(':1') if x])
            download_url = 'http://down.diyifanwen.com/kejianfiles' + download_url
        else:
            download_url = ''
        yield DocumentItem(
            title=title,
            download_url=download_url,
            post_url=response.url,
            directory=directory,
        )
