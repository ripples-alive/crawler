# -*- coding: utf-8 -*-
import scrapy

from jianlimoban.items import JianlimobanItem


class JianliSpider(scrapy.Spider):
    name = "jianli"
    allowed_domains = ["www.jianli-moban.com"]
    start_urls = (
        'http://www.jianli-moban.com/c20.aspx',
        'http://www.jianli-moban.com/c22.aspx',
    )

    def parse(self, response):
        template_list = response.xpath(
            '//table[@id="dlNews"]//td//a/@href').extract()
        for path in template_list:
            yield scrapy.Request(response.urljoin(path), self.parse_template)

        next_page = response.css(u'div.pager a[title="后页"]').xpath(
            '@href').extract_first()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page), self.parse)

    def parse_template(self, response):
        download_list = response.xpath(
            '//ul[@id="softLinks"]//li//a/@href').extract()
        if not download_list:
            download_list = response.xpath('//div[@id="content"]//a[contains(@href, "upload/")]/@href').extract() \
                + response.xpath('//div[@id="content"]//a[contains(@href, "down/")]/@href').extract() \
                + response.xpath('//div[@id="content"]//a[contains(@href, "download/")]/@href').extract()
        title = response.xpath('//h1[@class="aTitle"]/text()').extract_first()
        for download_path in download_list:
            return JianlimobanItem(page=response.url, name=title, url=response.urljoin(download_path))
