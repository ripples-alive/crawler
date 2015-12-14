# -*- coding: utf-8 -*-
import scrapy

from topit.items import PictureItem


class PictureSpider(scrapy.Spider):
    name = "picture"
    allowed_domains = ["www.topit.me"]
    start_urls = (
        'http://www.topit.me/items/search?query=%E7%AC%91',
    )

    def parse(self, response):
        img_list = response.xpath("//div[@class='catalog']//img")
        for img in img_list:
            inner_url = response.urljoin(img.xpath("../@href").extract_first())
            yield scrapy.Request(inner_url, self.parse_inner, cookies={'is_click': 1})

        next_url = response.xpath("//a[@id='page-next']/@href").extract_first()
        if next_url is not None:
            yield scrapy.Request(response.urljoin(next_url), self.parse)

    def parse_inner(self, response):
        # print response.xpath(u"//div[@id='content']//i[text()='下载原图']")
        url = response.xpath(u"//div[@id='content']//a[@download]/@href").extract_first()
        yield PictureItem(image_urls=[url])
