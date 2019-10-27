# -*- coding: utf-8 -*-
import scrapy
import json
import re
import time
import datetime

from scrapy.conf import settings
from crawler_news.items import CrawlerNewsItem
from crawler_news.items import CrawlerNewsCommentItem


class VejaSpider(scrapy.Spider):
    name = 'veja'
    allowed_domains = ['veja.abril.com.br']
    start_urls = []

    def __init__(self, *a, **kw):
        super(VejaSpider, self).__init__(*a, **kw)
        with open('start_urls/veja.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        def status_urls(url):
            with open('start_urls/veja.json') as json_file:
                data = json.load(json_file)
            for key, value in data.items():
                if key in response.request.url:
                    data[key] = response.request.url
                    with open('start_urls/veja.json', 'w') as outfile:  
                        json.dump(data, outfile)
                    break

        status_urls(response.request.url)

        # get json by Jquery
        jsonresponse = json.loads(response.body_as_unicode())
        current_day = self.format_day(jsonresponse['currentday'][:6]+'20'+jsonresponse['currentday'][6:]) 
        if current_day >= self.format_day(settings['DEADLINE']):
            for article_link in jsonresponse['postflair']:
                yield response.follow(article_link, self.parse_article)

            # get next_page  
            delimiters_url = u'[^0-9]'
            next_page = int(re.sub(delimiters_url, ' ', response.request.url).split()[0]) + 1
            yield response.follow('https://veja.abril.com.br/?infinity=infinite_scroll&page=' + str(next_page) + '&order=DESC', self.parse)

    def parse_article(self, response):
        # get title
        title = response.css('h1.article-title::text').extract_first()
        # get sub_title
        sub_title = response.css('h2.article-subtitle::text').extract_first()
        # get article's date
        date = self.format_date(response.css('div.article-date span::text').extract_first())
        # get author
        author = response.css('div.article-author span::text').extract_first()
        # get text
        text = ""
        for paragraph in response.xpath("//section[@class='article-content']/p//text()").extract():
            text = text + paragraph
        # get section
        section = response.css('div.article-category a::text').extract_first()  

        news = CrawlerNewsItem(
        _id=response.request.url,title=title, sub_title=sub_title, date=date,
        author=author, text=text, section=section, url=response.request.url)
        
        yield news

        # get comments
        for (text_comment,dt_comment, author_comment) in zip(response.css('div.comment-text p::text'),
            response.css('span.comment-meta.comment-metadata a::text'), response.css('div.comment-author.vcard cite::text')):
            comment = CrawlerNewsCommentItem(
              date=self.format_date(dt_comment.extract()), # transform comments' date from isodate to timestamp
              author=author_comment.extract(),
              text=text_comment.extract(), 
              id_article=response.request.url)

            yield comment

    def format_date(self,date):
        def get_mes(mes_string):
            dic = {'jan': '01', 'fev': '02', 'mar': '03', 'abr': '04', 'maio': '05', 
            'jun': '06', 'jul': '07', 'ago': '08', 'set': '09', 'out': '10', 'nov': '11', 'dez': '12'}
            return dic[mes_string]

        delimiters_date = u'[^a-zA-Z0-9]'
        date_list = re.sub(delimiters_date, ' ', date).split()
        date_string_format = date_list[0] + '.' + get_mes(date_list[1]) + '.' + date_list[2] + '-' + date_list[3]
        return int(time.mktime(datetime.datetime.strptime(date_string_format, "%d.%m.%Y-%Hh%M").timetuple()))

    def format_day(self, date):
        timestamp = int(time.mktime(datetime.datetime.strptime(date, "%d.%m.%Y").timetuple()))
        return int(timestamp)