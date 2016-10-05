# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response

from duxiu.items import ExamItem


class ExamSpider(scrapy.Spider):
    name = "exam"
    allowed_domains = ["book.duxiu.com"]
    start_urls = (
        'http://book.duxiu.com/examindex.jsp',
    )

    def parse(self, response):
        for one_level in response.xpath('//ul[@class="treeBd"]/li'):
            one_level_title = one_level.xpath(
                './div/a[contains(@href, "?fenlei=")]/text()').extract_first()
            for two_level in one_level.xpath('./ul/li'):
                two_level_title = two_level.xpath(
                    './div/a[contains(@href, "?fenlei=")]/text()').extract_first()
                for three_level in two_level.xpath('./ul/li'):
                    three_level_title = three_level.xpath(
                        './a[contains(@href, "?fenlei=")]/text()').extract_first()
                    url = three_level.xpath(
                        './a[contains(@href, "?fenlei=")]/@href').extract_first()
                    classification = [one_level_title,
                                      two_level_title, three_level_title]
                    classification = map(
                        lambda x: x.split('(')[0], classification)
                    yield scrapy.Request(response.urljoin(url), self.parse_list, meta={'classification': classification})

    def parse_list(self, response):
        next_page_url = response.xpath(
            u'//div[@id="pageinfo"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url), self.parse_list, meta=response.meta)

        for download_dom in response.xpath('//ul[@class="searchResult"]/li/div[1]/a[1]'):
            url = download_dom.xpath('./@href').extract_first()
            title = download_dom.xpath('./text()').extract_first()
            yield ExamItem(url=response.urljoin(url),
                           title=title,
                           classification=response.meta['classification'])
