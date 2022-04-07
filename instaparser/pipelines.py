# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from scrapy.pipelines.images import ImagesPipeline
import scrapy
from pymongo.errors import DuplicateKeyError

class InstaparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.instagram

    def process_item(self, item, spider):
        if item.__class__.__name__ == 'InstaparserItem':
            collection = self.mongo_base['instagram']
            try:
                collection.insert_one(item)  # Добавляем в базу данных
                print('Post added to my collections')
            except DuplicateKeyError:
                print(f'Post {item["_id"]} is already exist')
        if item.__class__.__name__ == 'InstaparserFollowItem':
            collection = self.mongo_base['instafollow']
            try:
                collection.insert_one(item)  # Добавляем в базу данных
                print('Follow user added to my collections')
            except DuplicateKeyError:
                print(f'Follow {item["_id"]} is already exist')
        return item


class InstaPhotosPipline(ImagesPipeline):
    def get_media_requests(self, item, info):
        if item.__class__.__name__ == 'InstaparserItem':
            img_req = item['photo']
            print(img_req)
            if img_req:
                try:
                    yield scrapy.Request(img_req, meta=item)
                except Exception as e:
                    print(e)

    def file_path(self, request, item, response=None, info=None):
        img_path = item['user_id']
        url = request.url.split('?')
        path = img_path + '/' + url[0].split('/')[-1]
        return path


    def item_completed(self, results, item, info):
        if item.__class__.__name__ == 'InstaparserItem':
            item['photo'] = [itm[1] for itm in results if itm[0]]
            return item
        else:
            return item
