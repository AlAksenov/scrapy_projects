# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient
from datetime import date
import re
from pymongo.errors import DuplicateKeyError


class JobparserPipeline:
    def __init__(self):
        client = MongoClient('localhost', 27017)
        self.mongo_base = client.vacancy1803

    def process_item(self, item, spider):
        print()
        # Обработка данных
        item['date_parse'] = str(date.today())
        item['_id'] = re.findall(r'\d+', item['url'])[0] + str(date.today())
        salary = item['salary']
        if spider.name == 'hhru':
            salary = ''.join(map(str, salary[:-1])).split(' ')
            if 'от' in salary:
                item['salary_min'] = int(salary[salary.index('от') + 1].replace('\xa0', ''))
                item['currency'] = salary[-1]
            if 'до' in salary:
                item['salary_max'] = int(salary[salary.index('до') + 1].replace('\xa0', ''))
                item['currency'] = salary[-1]
        if spider.name == 'sjru':
            if '—' in salary:
                item['salary_min'] = int(salary[salary.index('—') - 2].replace('\xa0', ''))
                item['salary_max'] = int(salary[salary.index('—') + 2].replace('\xa0', ''))
                item['currency'] = salary[-3]
            elif 'от' in salary:
                item['salary_min'] = re.findall(r'\d+', salary[salary.index('от') + 2].replace('\xa0', ''))[0]
                item['currency'] = re.findall(r'\D+', salary[salary.index('от') + 2].replace('\xa0', ''))[0]
            elif 'до' in salary:
                item['salary_max'] = re.findall(r'\d+', salary[salary.index('до') + 2].replace('\xa0', ''))[0]
                item['currency'] = re.findall(r'\D+', salary[salary.index('до') + 2].replace('\xa0', ''))[0]
            elif salary[0].replace('\xa0', '').isdigit():
                item['salary_min'] = int(salary[0].replace('\xa0', ''))
                item['salary_max'] = int(salary[0].replace('\xa0', ''))
                item['currency'] = salary[2]

        collection = self.mongo_base[spider.name]
        try:
            collection.insert_one(item)
        except DuplicateKeyError:
            print(f'Vacancy {item["_id"]} is already exist')

        return item
