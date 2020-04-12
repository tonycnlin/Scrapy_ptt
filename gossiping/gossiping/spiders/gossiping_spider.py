# -*- coding: utf-8 -*-
import scrapy
from gossiping.items import GossipingItem
import time
import logging
from scrapy.http import FormRequest
from scrapy.selector import Selector
import sys
class GossipingSpiderSpider(scrapy.Spider):
    name = 'gossiping_spider'
    allowed_domains = ['ptt.cc']
    start_urls = ['http://www.ptt.cc/bbs/Gossiping/index.html']

    _retries = 0
    MAX_RETRY = 1
    _pages = 0
    MAX_PAGES = 7

    def parse(self, response):
        #通過滿18驗證
        if len(response.xpath('//div[@class="over18-notice"]')) > 0:
            if self._retries < GossipingSpiderSpider.MAX_RETRY:
                self._retries += 1
                logging.warning('retry {} times...'.format(self._retries))
                yield FormRequest.from_response(response,
                                                formdata={'yes': 'yes'},
                                                callback=self.parse_article)
            else:
                logging.warning('you cannot pass')

        else:
            while self._pages < GossipingSpiderSpider.MAX_PAGES:
                self._pages += 1
              
                
                print('======next======')
                next_page = response.xpath(
                    '//div[@id="action-bar-container"]//a[contains(text(), "上頁")]/@href')
                if next_page:
                    url = response.urljoin(next_page[0].extract())
                    yield scrapy.Request(url, self.parse_article)
                else:
                    logging.warning('===================no next page=================')
                
                    

        
        
    def parse_article(self, response):
        item = GossipingItem()
        target = response.xpath("//div[@class='r-ent']")
        
        logging.warning('===============    def parse_article(self, response):==================')
        
        for tag in target:
            print(tag)
            try:
                item['title'] = tag.css("div.title a::text")[0].extract()
                item['author'] = tag.css('div.author::text')[0].extract()
                item['date'] = tag.css('div.date::text')[0].extract()
                item['push'] = tag.css('span::text')[0].extract()
                item['url'] = tag.css('div.title a::attr(href)')[0].extract()
               
                yield item

            except:
                logging.warning(f'====={sys.exc_info()[0]}======')
               
                pass

        self._pages += 1
        print('======next======')
        next_page = response.xpath(
            '//div[@id="action-bar-container"]//a[contains(text(), "上頁")]/@href')
        if next_page:
            url = response.urljoin(next_page[0].extract())
            if self._pages < GossipingSpiderSpider.MAX_PAGES:
                yield scrapy.Request(url, self.parse_article)
        
        