# -*- coding: utf-8 -*-
import scrapy

from zlunwen.items import PaperItem


class PaperSpider(scrapy.Spider):
    name = "paper"
    allowed_domains = ["www.zlunwen.com"]
    start_urls = (
        'http://www.zlunwen.com/',
    )

    def parse(self, response):
        for nav_dom in response.xpath('//div[@class="nav"]'):
            main_class = nav_dom.xpath('.//dt/a/text()').extract_first()
            for dd_dom in nav_dom.xpath('.//dd'):
                sub_class = dd_dom.xpath('./a/text()').extract_first()
                url = dd_dom.xpath('./a/@href').extract_first()
                yield scrapy.Request(response.urljoin(url), self.parse_list,
                                     meta={'main_class': main_class, 'sub_class': sub_class})

    def parse_list(self, response):
        next_url = response.xpath(u'//div[contains(@class, "page")]//a[text()="下一页"]/@href').extract_first()
        if next_url is not None and next_url != '#':
            yield scrapy.Request(response.urljoin(next_url), self.parse_list, meta=response.meta)

        for url in response.xpath('//div[@class="l"]//li[@class="title"]/a/@href').extract():
            yield scrapy.Request(response.urljoin(url), self.parse_post, meta=response.meta)

    def parse_post(self, response):
        url = response.xpath('//ul[@class="ll"]//a/@href').extract_first()
        title = response.xpath('//div[@class="title"]/text()').extract_first()
        yield PaperItem(url=response.urljoin(url),
                        title=title,
                        post_url=response.url,
                        main_class=response.meta['main_class'],
                        sub_class=response.meta['sub_class'])
