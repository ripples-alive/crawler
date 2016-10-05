# -*- coding: utf-8 -*-
import scrapy
from topsage.items import ComputerItem


class ComputerSpider(scrapy.Spider):
    name = "computer"
    allowed_domains = ["club.topsage.com"]
    start_urls = (
        'http://club.topsage.com/forum-49-1.html',
    )

    def parse(self, response):
        for path in response.xpath('//*[contains(@id, "forum_")]/table//td/h2/a/@href').extract():
            yield scrapy.Request(response.urljoin(path), self.parse_list)

    def parse_list(self, response):
        next_path = response.xpath('//*[@id="fd_page_bottom"]//a[@class="nxt"]/@href').extract_first()
        if next_path is not None:
            yield scrapy.Request(response.urljoin(next_path), self.parse_list)

        for path in response.xpath('//table[@id="threadlisttableid"]/tbody/tr/th/a[contains(@href, "topsage")]/@href').extract():
            yield scrapy.Request(response.urljoin(path), self.parse_post)

    def parse_post(self, response):
        post_title = response.xpath('//*[@id="thread_subject"]/a/text()').extract_first()
        for a_dom in response.xpath('//div[@class="pct"]//a'):
            yield ComputerItem(post_url=response.url, post_title=post_title,
                url=a_dom.xpath('@href').extract_first(),
                name=a_dom.xpath('text()').extract_first())
