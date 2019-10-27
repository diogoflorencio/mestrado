# -*- coding: utf-8 -*-
import scrapy
import dateutil.parser
import json

from crawler_news.items import CrawlerNewsItem
from crawler_news.items import CrawlerNewsCommentItem


class FolhaSpider(scrapy.Spider):
	name = 'folha'
	allowed_domains = ['folha.uol.com.br']
	start_urls = []

	def __init__(self, *a, **kw):
		super(FolhaSpider, self).__init__(*a, **kw)
		with open('start_urls/folha.json') as json_file:
			data = json.load(json_file)
		self.start_urls = list(data.values())

	def parse(self, response):
		def status_urls(url):
			with open('start_urls/folha.json') as json_file:
				data = json.load(json_file)
			for key, value in data.items():
				if key in response.request.url:
					data[key] = response.request.url
					with open('start_urls/folha.json', 'w') as outfile:
						json.dump(data, outfile)
					break

		status_urls(response.request.url)

		for article in response.css("div.c-headline__content a::attr(href)"):
			yield response.follow(article.extract(), self.parse_article)
		# get more articles
		next_page = response.css('li.c-pagination__arrow a::attr(href)')
		if next_page is not None:
			yield response.follow(next_page[len(next_page)-1], self.parse)

	def parse_article(self, response):
		# get title
		title = response.css('h1.c-content-head__title::text').extract_first()
		# get sub_title
		sub_title = response.css('h2.c-content-head__subtitle::text').extract_first()
		# get article's date transform date from isodate to timestamp
		date = dateutil.parser.parse(response.css('time.c-more-options__published-date::attr(datetime)').extract_first()).strftime('%s')
		# get author
		author = response.css('strong.c-signature__author::text').extract_first()
		# get text
		text = ""
		for paragraph in response.xpath("//div[@class='c-news__body']/p//text()").extract():
			text = text + paragraph
		# get section
		section = response.css('li.c-site-nav__item.c-site-nav__item--section a::text').extract_first()

		article = CrawlerNewsItem(_id=response.request.url,title=title, sub_title=sub_title, date=date, author=author, text=text, section=section, url=response.request.url)

		yield article
