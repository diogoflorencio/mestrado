# -*- coding: utf-8 -*-
import scrapy
import json
import time
import datetime

from crawler_news.items import CrawlerNewsItem
from crawler_news.items import CrawlerNewsCommentItem


class GazetaDoPovoSpider(scrapy.Spider):
	name = 'gazeta_do_povo'
	allowed_domains = ['gazetadopovo.com.br']
	start_urls = [
	'https://gazetadopovo.com.br/politica/',
	'https://www.gazetadopovo.com.br/economia/',
	'https://www.gazetadopovo.com.br/mundo/',
	'https://www.gazetadopovo.com.br/justica/',
	'https://www.gazetadopovo.com.br/educacao/']

	token = ""

	def parse(self, response):
		for article in response.css("article"):
			link_article = 'https://gazetadopovo.com.br' + str(article.css("a::attr(href)").extract_first())
			yield response.follow(link_article, self.parse_article)
		# get more articles
		next_page = 'https://gazetadopovo.com.br' + str(response.css('a[title="Próxima página"]::attr(href)').extract_first())
		if next_page is not None:
			yield response.follow(next_page, self.parse)

	def parse_article(self, response):
		# get title
		title = response.css('h1.gp-coluna.col-8.c-titulo ::text').extract_first()
		# get sub_title
		sub_title = response.css('h2.c-sumario ::text').extract_first()
		# get author
		author = response.css('li.c-autor span::text').extract_first()
		# get date
		date = self.format_date(response.css('li.data-publicacao time::text').extract_first())
		# get section
		section = response.css('a.c-nome-editoria span::text').extract_first()
		# get text
		text=""
		for paragraph in response.css('div.gp-coluna.col-6.texto-materia.paywall-google p::text'):
			text = (text + paragraph.extract())
		
		# get comments
		self.token = response.css('div.sociabilizacao-load-area ::attr(data-token)').extract_first()
		link_comments = 'https://live.gazetadopovo.com.br/webservice/comentario/abaComentarios?comentario=&token=' + self.token
		yield response.follow(link_comments, self.parse_comments)

		article = CrawlerNewsItem(title=title, sub_title=sub_title, author=author, date=date, text=text, section=section, _id=response.request.url)

		yield article

	def parse_comments(self, response):
		jsonresponse = json.loads(response.body_as_unicode())
		for article_comment in jsonresponse['delivery']['comentarios']:
			commment = CrawlerNewsCommentItem(
				id_article=article_comment['materia_url'], 
				date=article_comment['data_comentario'],
				author=article_comment['tooltip_nome_exibicao'], 
				text=article_comment['comentario'],
				hash_user=article_comment['tooltip_usuario_hash'])

			yield commment
		#  get more comments
		if jsonresponse['delivery']['paginacao']['proxima'] is not False:
			link_more_comments = 'https://live.gazetadopovo.com.br/webservice/comentario/abaComentarios?offset=' + str(jsonresponse['delivery']['paginacao']['proxima'])+'&comentario=&token=' + self.token
			yield response.follow(link_more_comments, self.parse_comments)

	def format_date(self, date):
		date_string_format = str(date)[1:-1] #problema
		print('\n\n\n\n'+date_string_format+'\n\n\n\n')
		timestamp = int(time.mktime(datetime.datetime.strptime(date_string_format, "%d/%m/%Y").timetuple()))
		return timestamp