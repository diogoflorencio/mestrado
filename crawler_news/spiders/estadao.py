# -*- coding: utf-8 -*-
import scrapy
import re
import json
import time
import datetime

from crawler_news.items import CrawlerNewsItem

class EstadaoSpider(scrapy.Spider):
    name = 'estadao'
    allowed_domains = ['estadao.com.br']
    page = 1
    start_urls = []

    def __init__(self, *a, **kw):
        super(EstadaoSpider, self).__init__(*a, **kw)
        with open('start_urls/estadao.json') as json_file:
            data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        def status_urls(url):
            with open('start_urls/estadao.json') as json_file:
                data = json.load(json_file)
            for key, value in data.items():
                if key in response.request.url:
                    data[key] = response.request.url
                    with open('start_urls/estadao.json', 'w') as outfile:
                        json.dump(data, outfile)
                    break
        status_urls(response.request.url)

        articles = response.css("a.link-title::attr(href)")

        for article in articles:
        	yield response.follow(article.extract(), self.parse_article)

        if articles:
            # get more articles
            next_page = response.request.url[:768] + str(self.page) + '&config%5Bbusca%5D%5Brows%5D=5&ajax=1'
            self.page += 1
            yield response.follow(next_page, self.parse)



    def parse_article(self, response):
        # get title
        title = response.css('h1.n--noticia__title::text').extract_first()
        # get sub_title
        sub_title = response.css('h2.n--noticia__subtitle::text').extract_first()
        # get article's date
        dt_article = response.css('div.n--noticia__state-desc p::text').extract_first()
        # transform article's date from isodate to timestamp
        dt_article = self.format_date(dt_article)
        # get article's section
        section = response.css('div.header-current-page.cor-e a::text').extract_first()
        # get author
        author = response.css('div.n--noticia__state-title::text').extract_first()
        # get text
        text_article = ""
        paragraph = ""
        for paragraph in response.css('div.n--noticia__content.content p::text').extract():
            text_article = text_article + paragraph

        article = CrawlerNewsItem(_id=response.request.url, title=title, sub_title=sub_title, date=dt_article, text=text_article, section=section, url=response.request.url)

        yield article

    def format_date(self,date):
        def get_mes(mes_string):
            dic = {'janeiro': '01', 'fevereiro': '02', 'março': '03', 'abril': '04', 'maio': '05',
            'junho': '06', 'julho': '07', 'agosto': '08', 'setembro': '09', 'outubro': '10', 'novembro': '11', 'dezembro': '12'}
            return dic[mes_string]

        date_list = date.split()
        date_string_format = date_list[0] + '.' + get_mes(date_list[2]) + '.' + date_list[4] + '-' + date_list[6]
        return int(time.mktime(datetime.datetime.strptime(date_string_format, "%d.%m.%Y-%Hh%M").timetuple()))
