import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from kbcbank.items import Article


class KbcSpider(scrapy.Spider):
    name = 'kbc'
    start_urls = ['https://newsroom.kbc.com/en']

    def parse(self, response):
        latest = response.xpath('//a[@class="latest-story-card__link"]/@href').get()
        yield response.follow(latest, self.parse_article)

        links = response.xpath('//a[@class="story-card__link"]/@href').getall()
        yield from response.follow_all(links, self.parse_article)

    def parse_article(self, response):
        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1[@class="story__title"]/text()').get()
        if title:
            title = title.strip()

        date = response.xpath('//span[@class="story-date"]/text()').get().split()[1:]
        if date:
            if date[-1] == '—':
                date.pop(-1)
            date = " ".join(date)
            date = datetime.strptime(date.strip(), '%B %d, %Y')
            date = date.strftime('%Y/%m/%d')

        content = response.xpath('//div[@class="story__column story__column--content"]//text()').getall()
        content = [text for text in content if text.strip()]
        content = "\n".join(content[3:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
