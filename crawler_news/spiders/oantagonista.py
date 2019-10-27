# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import json

from crawler_news.items import CrawlerNewsItem
from crawler_news.items import CrawlerNewsCommentItem


class OantagonistaSpider(scrapy.Spider):
    name = 'oantagonista'
    allowed_domains = ['oantagonista.com']
    start_urls = []

    def __init__(self, *a, **kw):
        super(OantagonistaSpider, self).__init__(*a, **kw)
        with open('start_urls/oantagonista.json') as json_file:
                data = json.load(json_file)
        self.start_urls = list(data.values())

    def parse(self, response):
        def status_urls(url):
            with open('start_urls/oantagonista.json') as json_file:
                data = json.load(json_file)
            for key, value in data.items():
                if key in response.request.url:
                    data[key] = response.request.url
                    with open('start_urls/oantagonista.json', 'w') as outfile:  
                        json.dump(data, outfile)
                    break

        status_urls(response.request.url)

        for article in response.css("a.article_link::attr(href)"):
            yield response.follow(article.extract(), self.parse_article)
        # get more articles
        next_page = response.css('link[rel=next]::attr(href)').extract_first()
        if next_page is not None:
            yield response.follow(next_page, self.parse)
	
    def parse_article(self, response):
        # get title
        title = response.css('h1::text').extract_first()
        # get article's date
        dt_article = response.css('time.entry-date.published::attr(datetime)').extract_first()
        # transform article's date from isodate to timestamp 
        dt_article = dateutil.parser.parse(dt_article).strftime('%s')
        # get article's section
        section = response.css('span.categoria a::text').extract_first()
        # get text
        text_article = ""
        for paragraph in response.xpath("//div[@class='entry-content']/p//text()").extract():
            text_article = text_article + paragraph

        article = CrawlerNewsItem(_id=response.request.url, title=title, date=dt_article, text=text_article, section=section)
        
        yield article
        
        # get comments
        for (text_comment,dt_comment, author_comment) in zip(response.css('div.comment-content p::text'),
            response.css('div.comment-metadata time::attr(datetime)'), response.css('div.comment-author.vcard b::text')):
            comment = CrawlerNewsCommentItem(
              date=dateutil.parser.parse(dt_comment.extract()).strftime('%s'), # transform comments' date from isodate to timestamp
              author=author_comment.extract(),
              text=text_comment.extract(), 
              id_article=response.request.url)

            yield comment