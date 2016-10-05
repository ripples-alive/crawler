# -*- coding: utf-8 -*-
import scrapy
from scrapy.shell import inspect_response

from paper.items import PaperItem


class ReleasepaperSpider(scrapy.Spider):
    name = "releasepaper"
    allowed_domains = ["www.paper.edu.cn"]
    start_urls = (
        'http://www.paper.edu.cn/releasepaper',
    )

    def parse(self, response):
        onelevel_url_list = response.xpath('//div[@id="xk"]//li/a/@href').extract()
        for onelevel_url in onelevel_url_list:
            yield scrapy.Request(response.urljoin(onelevel_url), self.parse_onelevel)

    def parse_onelevel(self, response):
        subject_url_list = response.xpath('//div[@id="tt"]//ul/li/a/@href').extract()
        for subject_url in subject_url_list:
            yield scrapy.Request(response.urljoin(subject_url), self.parse_subject)

    def parse_subject(self, response):
        next_page_url = response.xpath(u'//div[@class="pages"]/a[text()="下一页"]/@href').extract_first()
        if next_page_url is not None:
            yield scrapy.Request(response.urljoin(next_page_url), self.parse_subject)
        content_url_list = response.xpath('//div[@class="cmtdiv"]/p[1]//a/@href').extract()
        # content_url_list = response.xpath(u'//span[text()="论文摘要："]/../a/@href').extract()
        for content_url in content_url_list:
            yield scrapy.Request(response.urljoin(content_url), self.parse_content)

    def parse_content(self, response):
        # inspect_response(response, self)
        classification = response.xpath('//div[@class="taxis_list"]/a[position()>1]/text()').extract()
        download_url = response.xpath(u'//t[text()="PDF全文下载："]/../../a/@href').extract_first()
        download_url = response.urljoin(download_url)
        title = response.xpath('//p[@class="title_02"]/text()').extract_first()
        english_title = response.xpath('//p[@class="title_03"]/text()').extract_first()
        yield PaperItem(url=download_url, classification=classification, title=title, english_title=english_title)
