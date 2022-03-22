# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class JobparserItem(scrapy.Item):
    # define the fields for your item here like:
    name = scrapy.Field()
    salary = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    currency = scrapy.Field()
    date_parse = scrapy.Field()
    _id = scrapy.Field()
    url = scrapy.Field()
    location = scrapy.Field()

