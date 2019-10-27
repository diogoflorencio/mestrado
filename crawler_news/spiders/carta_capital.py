# -*- coding: utf-8 -*-
import scrapy
import time
import datetime
import json

from crawler_news.items import CrawlerNewsItem


class CartaCapitalSpider(scrapy.Spider):
    name = 'carta_capital'
    allowed_domains = ['cartacapital.com.br']
    start_urls = []

    def __init__(self, *a, **kw):
        super(CartaCapitalSpider, self).__init__(*a, **kw)
        with open('output/carta_capital.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        def status_output(url):
            with open('output/carta_capital.json') as json_file:
                data = json.load(json_file)
            for key, value in data.items():
                if key in response.request.url:
                    data[key] = response.request.url
                with open('output/carta_capital.json', 'w') as outfile:  
                    json.dump(data, outfile)
                break

        status_output(response.request.url)

        for article_link in response.css("h3.eltdf-pt-three-title a::attr(href)"):
            yield response.follow(article_link.extract(), self.parse_article)
        # get more articles
        next_page = response.css('div.eltdf-btn.eltdf-bnl-load-more.eltdf-load-more.eltdf-btn-solid a::attr(href)').extract_first()
        if next_page is not None:
	        yield response.follow(next_page, self.parse)

        

    def parse_article(self, response):
        # get title
        title = response.css('h1.eltdf-title-text ::text').extract_first()
        # get sub_title
        sub_title = response.css('div.wpb_wrapper h3::text').extract_first()
        # get article's date
       	date = self.format_date(response.css('div.eltdf-post-info-date.entry-date.updated a::text').extract_first())
        # get author
        author = response.css('a.eltdf-post-info-author-link ::text').extract_first()
        # get text
        text = ""
        for paragraph in response.css('div.eltdf-post-text p::text'):
            text = (text + paragraph.extract())
        # get section
        section = response.css('div.eltdf-post-info-category a::text').extract_first()

        news = CrawlerNewsItem(
        title=title, sub_title=sub_title, date=date,
        author=author, text=text, section=section, _id=response.request.url)

        yield news

    def format_date(self, date):
        def get_mes(mes_string):
            dic = {'janeiro': '01', 'fevereiro': '02', u'mar\xe7o': '03', 'abril': '04', 'maio': '05', 
            'junho': '06', 'julho': '07', 'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'}
            return dic[mes_string]

        def format_dia(dia):
            if(len(dia)==1):
                dia = '0'+dia
            return dia

        date = date.split()
        date_string_format = format_dia(date[0]) + "/" + get_mes(date[2]) + "/" + date[4]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_string_format, "%d/%m/%Y").timetuple()))
        return timestamp

    def get_start_urls(self):
        with open('/home/diogo/workspace/crawler_news/crawler_news/spiders/output/carta_capital.json') as json_file:
                data = json.load(json_file)
        return list(data.values())