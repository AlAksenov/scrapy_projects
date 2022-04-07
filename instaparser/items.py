# -*- coding: utf-8 -*-
# Define here the models for your scraped items
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import MapCompose, Compose, TakeFirst

class InstaparserItem(scrapy.Item):
    _id = scrapy.Field()
    likes = scrapy.Field()
    post = scrapy.Field()
    username = scrapy.Field()
    photo = scrapy.Field()
    user_id = scrapy.Field()

class InstaparserFollowItem(scrapy.Item):
    _id = scrapy.Field()
    username_follow = scrapy.Field()
    photo_follow = scrapy.Field()
    fullname_follow = scrapy.Field()
    username = scrapy.Field()
    follow_type = scrapy.Field()
    follow_user_id = scrapy.Field()


