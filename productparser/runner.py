from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from productparser import settings
from productparser.spiders.lerua import LeruaSpider


if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)

    process = CrawlerProcess(settings=crawler_settings)
    # query = input('')
    process.crawl(LeruaSpider, search='q-mac-book-pro-16')

    process.start()