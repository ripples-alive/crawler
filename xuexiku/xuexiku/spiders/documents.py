# -*- coding: utf-8 -*-
import scrapy
from xuexiku.items import DocumentItem


class DocumentsSpider(scrapy.Spider):
    name = "documents"
    allowed_domains = ["www.xuexiku.com.cn"]
    start_urls = (
        'http://www.xuexiku.com.cn/Index.html',
    )

    def parse(self, response):
        item = DocumentItem()
        for category_dom in response.xpath("//div[@class='nav']//td//ul//li//a"):
            path = category_dom.xpath('./@href').extract_first()
            category = category_dom.xpath('./text()').extract_first()
            item['category'] = category
            yield scrapy.Request(response.urljoin(path), self.parse_doc_list, meta={'item': item.copy()})

    def parse_doc_list(self, response):
        item = response.meta['item']
        for path in response.xpath(u"//ul[@class='mlist']//a[text()='下载']/@href").extract():
            yield scrapy.Request(response.urljoin(path), self.parse_doc, meta={'item': item.copy()})

        selector = u"//div[@class='pagelist1']//a[contains(text(), '下一页')]/@href"
        next_path = response.xpath(selector).extract_first()
        if next_path is not None:
            yield scrapy.Request(response.urljoin(next_path), self.parse_doc_list, meta={'item': item.copy()})

    def parse_doc(self, response):
        item = response.meta['item']
        item['name'] = response.xpath("//div[@class='info']//h2//strong/text()").extract_first()
        for link in response.xpath("//div[@class='downlist']//td/child::a"):
            item['link'] = link.xpath('./@href').extract_first()
            item['filename'] = link.xpath('./text()').extract_first()
            yield item.copy()
