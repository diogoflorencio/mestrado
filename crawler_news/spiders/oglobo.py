# -*- coding: utf-8 -*-
import scrapy
import json
import time
import datetime
import dateutil.parser

from crawler_news.items import CrawlerNewsItem
from crawler_news.items import CrawlerNewsCommentItem
from crawler_news.items import CrawlerNewsMetaDataItem


class OgloboSpider(scrapy.Spider):
    name = 'oglobo'
    allowed_domains = ['oglobo.globo.com']
    start_urls = []

    def __init__(self, *a, **kw):
        super(OgloboSpider, self).__init__(*a, **kw)
        with open('start_urls/oglobo.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())


    def parse(self, response):
        def status_urls(url):
            with open('start_urls/oglobo.json') as json_file:
                data = json.load(json_file)
            for key, value in data.items():
                if key in response.request.url:
                    data[key] = response.request.url
                    with open('start_urls/oglobo.json', 'w') as outfile:  
                        json.dump(data, outfile)
                    break

        status_urls(response.request.url)
        
        # get just json from ogloboAPI
        jsonresponse = json.loads(response.body_as_unicode())[0]
        for article in jsonresponse['conteudos']:
            if article['informePublicitario'] is False:
                metadata_article = CrawlerNewsMetaDataItem(_id=article['id'], subscribersOnly=article['exclusivoAssinantes'])
                yield metadata_article
                yield response.follow(article['url'], self.parse_article)

        # get more articles
        if jsonresponse['paginacao']['temProxima'] is True:
            yield response.follow('https://' + jsonresponse['paginacao']['urlProxima'], self.parse)

    def parse_article(self, response):
        # get title
        title = response.css('h1.article__title::text').extract_first()
        # get sub_title
        sub_title = response.css('h2.article__subtitle::text').extract_first()
        # get article's date
        date = self.format_date(str(response.css('div.article__date::text').extract_first()))
        # get author
        author = response.css('div.article__author::text').extract_first()
        # get text
        text = ""
        for paragraph in response.css('div.article__content-container.protected-content p::text'):
            text = (text + paragraph.extract())
        # get section
        section = response.css('div.site-header__section-name a::text').extract_first()
        # get id_article
        id_article = response.request.url.split('-')
        
        news = CrawlerNewsItem(
        _id=id_article[len(id_article)-1] ,title=title, sub_title=sub_title, date=date,
        author=author, text=text, section=section, url=response.request.url)

        yield news

        # get comments by json
        yield response.follow('https://oglobo.globo.com/ajax/comentario/buscar/' + id_article[len(id_article)-1] + '/1.json', self.parse_comments)
        
        
    def parse_comments(self, response):
        id_article = response.request.url.split('/')
        jsonresponse = json.loads(response.body_as_unicode())
        for article_comment in jsonresponse['comentarios']:
            comment = CrawlerNewsCommentItem(
              id_article=id_article[len(id_article)-2],
              date=dateutil.parser.parse(article_comment['dataNoHtml']).strftime('%s'), # transform comments' date from isodate to timestamp
              author=article_comment['autor'],
              text=article_comment['mensagem'])

            yield comment

        # get next comments' page
        if jsonresponse['temProximaPagina'] is True:
            yield response.follow(jsonresponse['urlProximaPagina'], self.parse_comments)

    def format_date(self, date):
        dt = date.split()
        date_string_format = dt[0]
        timestamp = int(time.mktime(datetime.datetime.strptime(date_string_format, "%d/%m/%Y").timetuple()))
        return timestamp
