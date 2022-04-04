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
        print(item['photo'])
        collection = self.mongo_base['instagram']
        try:
            collection.insert_one(item)  # Добавляем в базу данных
            print('Added to my collections')
        except DuplicateKeyError:
            print(f'Post {item["_id"]} is already exist')
        return item


class InstaPhotosPipline(ImagesPipeline):
    def get_media_requests(self, item, info):
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
        item['photo'] = [itm[1] for itm in results if itm[0]]
        return item

# # в info содержиться информация о том, сколько прилетело фотографий, сколько скачано, сколько стоит на очереди
# class LeroymerlinPhotosPipeline(ImagesPipeline):
#     def get_media_requests(self, item, info):
#         # проверяем есть ли фото
#         if item['photos']:
#             for img in item['photos']:
#                 try:
#                     # сюда прилетает уже очищеная ссылка
#                     yield scrapy.Request(img, meta=item)   # Скачиваем фото и передает item через meta
#                 except Exception as e:
#                     print(e)
#
#     """ метод определяющий путь куда складывать файлы, но метод не принимает item вообще. но
#     есть meta в scrapy.Request, который можно принять здесь. Нужно посмотреть в документации как
#     принимать. Можно выташить url из приходящего request и например из файла """
#     def file_path(self, request, response=None, info=None):
#         return f"{request.meta['name']}/{os.path.basename(urlparse(request.url).path)}"
#
#     def item_completed(self, results, item, info):
#         if results:
#             item['photos'] = [itm[1] for itm in results if itm[0]]
#         return item  # возвращаем изменённый item в return чтобы пайплайны следовали друг за другом