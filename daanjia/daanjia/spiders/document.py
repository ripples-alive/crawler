# -*- coding: utf-8 -*-
import json

import scrapy

from daanjia.items import DocumentItem


class DocumentSpider(scrapy.Spider):
    name = "document"
    allowed_domains = ["www.daanjia.com", "vdisk.weibo.com"]
    start_urls = (
        'http://www.daanjia.com/forum.php?gid=1',
    )

    def parse(self, response):
        for class_dom in response.xpath('//table[@class="fl_tb"]//td//dl/dt/a'):
            url = class_dom.xpath('./@href').extract_first()
            yield scrapy.Request(response.urljoin(url), callback=self.parse_catalog)

    def parse_catalog(self, response):
        page_dom = response.xpath('//div[@class="pg"]')[0]
        next_url = page_dom.xpath('./a[@class="nxt"]/@href').extract_first()
        if next_url is not None:
            yield scrapy.Request(response.urljoin(next_url), callback=self.parse_catalog)

        post_list = response.xpath('//table[@id="threadlisttableid"]//th/a[2]/@href').extract()
        assert next_url is None or len(post_list) == 20
        for post_url in post_list:
            yield scrapy.Request(response.urljoin(post_url), callback=self.parse_post)

    def parse_post(self, response):
        directory = '/'.join(response.xpath('//div[@id="pt"]//a/text()').extract()[2:-1])

        download_dom_list = response.xpath('//div[@id="postlist"]/div[1]//*[@class="attnm"]/a')
        if len(download_dom_list) != 0:
            for download_dom in download_dom_list:
                download_url = response.urljoin(download_dom.xpath('./@href').extract_first())
                filename = download_dom.xpath('./text()').extract_first()
                item = DocumentItem(
                    filename=filename,
                    download_url=download_url,
                    post_url=response.url,
                    directory=directory,
                )
                yield item
        else:
            for vdisk_url in response.xpath('//div[@id="postlist"]/div[1]//a[contains(@href, "vdisk")]/@href').extract():
                item = DocumentItem(
                    # filename=vdisk_url,
                    download_url=vdisk_url,
                    post_url=response.url,
                    directory=directory,
                )
                yield scrapy.Request(vdisk_url, callback=self.parse_vdisk, meta={'item': item})

    def parse_vdisk(self, response):
        item = response.meta['item']
        data_info = response.xpath('//a[@id="download_small_btn"]/@data-info').extract_first()
        if data_info is None:
            return
        filename = json.loads(data_info)['filename']
        item['filename'] = filename
        yield item
        # if self.start_urls: scrapy.shell.inspect_response(response, self); self.start_urls = (); raise scrapy.exceptions.CloseSpider()

