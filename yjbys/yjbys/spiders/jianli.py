# -*- coding: utf-8 -*-
import scrapy

from yjbys.items import YjbysItem


class JianliSpider(scrapy.Spider):
    name = "jianli"
    allowed_domains = ["jianlimoban.yjbys.com", "jianli.yjbys.com"]
    start_urls = (
        'http://jianli.yjbys.com/jianlixiazai/',
        'http://jianli.yjbys.com/jianlixiazai/jianlibiaogexiazai/',
    )

    def parse(self, response):
        download_list = response.xpath("//div[@id='mainleft']//ul[@class='listimg']//li")
        for one in download_list:
            name = one.xpath(".//a[@class='atext']/text()").extract_first()
            path = one.xpath(".//input/@onclick").extract_first()
            path = path.lstrip("window.open('").rstrip("')")
            yield YjbysItem(name=name, url=response.urljoin(path))

        next_page = response.xpath(u"//ul[@id='page_slice']//a[text()='下一页']/@href").extract_first()
        if next_page is not None:
            yield scrapy.Request(response.urljoin(next_page), self.parse)
