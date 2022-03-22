import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem


class SjruSpider(scrapy.Spider):
    name = 'sjru'
    allowed_domains = ['superjob.ru']
    search_word = 'python'
    start_urls = [f'https://russia.superjob.ru/vacancy/search/?keywords={search_word}']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@rel='next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[@class='jNMYr GPKTZ _1tH7S']//@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name_value = response.css('h1::text').get()
        salary_value = response.xpath("//span[@class='_1OuF_ ZON4b']//text()").getall()
        url_value = response.url
        location_value = response.xpath('//div[@class="f-test-address _3AQrx"]//text()').get()
        yield JobparserItem(name=name_value, salary=salary_value, url=url_value, location=location_value)
