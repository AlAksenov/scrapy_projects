import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://izhevsk.hh.ru/search/vacancy?area=1&search_field=name&search_field=company_name&search_field=description&text=python',
                  'https://izhevsk.hh.ru/search/vacancy?area=2&search_field=name&search_field=company_name&search_field=description&text=python']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@data-qa='pager-next']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//a[@data-qa='vacancy-serp__vacancy-title']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)


    def vacancy_parse(self, response: HtmlResponse):
        name_value = response.css('h1::text').get()
        salary_value = response.xpath("//div[@data-qa='vacancy-salary']//text()").getall()
        location_value = response.xpath("//p[@data-qa='vacancy-view-location']//text()").get()
        url_value = response.url
        yield JobparserItem(name=name_value, salary=salary_value, url=url_value, location=location_value)
