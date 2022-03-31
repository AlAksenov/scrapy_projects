import scrapy
from scrapy.http import HtmlResponse
from productparser.items import LeruaSpiderItem
from scrapy.loader import ItemLoader


class LeruaSpider(scrapy.Spider):
    name = 'lerua'
    allowed_domains = ['olx.kz']

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.start_urls = [f"https://www.olx.kz/list/{kwargs.get('search')}/"]
        self.page = 2

    def parse(self, response: HtmlResponse):

        next_page = response.xpath("//a[contains(@class, 'link pageNextPrev {page:" + str(self.page) + "}')]/@href").get()
        if next_page:
            self.page += 1
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//td/a/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        loader = ItemLoader(item=LeruaSpiderItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_xpath("name", "//h1/text()")
        loader.add_xpath("price", "//h3/text()")
        loader.add_xpath("description", "//div[@class = 'css-g5mtbi-Text']")
        loader.add_xpath("photos", "//div[@class='swiper-zoom-container']//@data-src")
        yield loader.load_item()

        # url = response.url
        # name = response.xpath("//h1/span/text()").get()
        # price = response.xpath("//span[@class='js-item-price']/text()").get()
        # photos = response.xpath("//div[@class='gallery-img-frame js-gallery-img-frame']/@data-url").getall()
        # yield AvitoparserItem(name=name, price=price, photos=photos, url=url)
