import re
from pymongo import MongoClient

# salary =  ['з/п не указана']
# salary = ['от ', '150\xa0000', ' ', 'руб.', ' на руки']
# salary =  ['до ', '220\xa0000', ' ', 'руб.', ' на руки']

salary = ["от ", "140 000", " до ", "200 000", " ", "руб.", " на руки"]
salary = ''.join(map(str, salary[:-1])).split(' ')

salary_min = None
salary_max = None
currency = None

if 'от' in salary:
    salary_min = int(salary[salary.index('от') + 1].replace('\xa0', ''))
    currency = salary[-1]
if 'до' in salary:
    salary_max = int(salary[salary.index('до') + 1].replace('\xa0', ''))
    currency = salary[-1]

print(salary_min)
print(salary_max)
print(currency)

from datetime import date

current_date = date.today()
print(current_date)

vacancy_link = 'https://russia.superjob.ru/vakansii/senior-python-backend-developer-40866744.html'

vacancy_id = re.findall(r'\d+', vacancy_link)[0] + str(date.today())
# print(vacancy_id[0] +str(current_date))
print(vacancy_id)

client = MongoClient('localhost', 27017)
mongo_base = client.vacancy1803
hhru = mongo_base.hhru
sjru = mongo_base.sjru
hhru.delete_many({})
sjru.delete_many({})

print('--------')

#salary = ['от', '\xa0', '120\xa0000\xa0руб.', '/', 'месяц']
salary = ['120\xa0000', '\xa0', '—', '\xa0', '150\xa0000', '\xa0', 'руб.', '/', 'месяц']
#salary = ['до', '\xa0', '70\xa0000\xa0руб.', '/', 'месяц']
#salary = ['По договорённости']
#salary = ['31\xa0500', '\xa0', 'руб.', '/', 'месяц']
#salary = ['от', '\xa0', '200\xa0000\xa0руб.', '/', 'месяц']
#salary = ["65 000", " ", "—", " ", "80 000", " ", "руб.", "/", "месяц"]




salary_min = None
salary_max = None
currency = None


if '—' in salary:
    salary_min = int(salary[salary.index('—') - 2].replace('\xa0', ''))
    salary_max = int(salary[salary.index('—') + 2].replace('\xa0', ''))
    currency = salary[-3]
elif 'от' in salary:
    salary_min = re.findall(r'\d+', salary[salary.index('от') + 2].replace('\xa0', ''))[0]
    currency = re.findall(r'\D+', salary[salary.index('от') + 2].replace('\xa0', ''))[0]
elif 'до' in salary:
    salary_max = re.findall(r'\d+', salary[salary.index('до') + 2].replace('\xa0', ''))[0]
    currency = re.findall(r'\D+', salary[salary.index('до') + 2].replace('\xa0', ''))[0]
elif salary[0].replace('\xa0', '').isdigit():
    salary_min = int(salary[0].replace('\xa0', ''))
    salary_max = int(salary[0].replace('\xa0', ''))
    currency = salary[2]




print(salary_min)
print(salary_max)
print(currency)


a = 'https://scontent-bos3-1.cdninstagram.com/v/t51.2885-15/277366355_655660869030170_2718908737345568088_n.jpg?stp=dst-jpg_e35_p1080x1080&_nc_ht=scontent-bos3-1.cdninstagram.com&_nc_cat=102&_nc_ohc=dL6WSzDdEWEAX-cCYA0&edm=APU89FABAAAA&ccb=7-4&oh=00_AT8DSpevoC_dLwAf1i-7_vl720g3Y1Z0AMdv-Lytut-JKg&oe=6252E7DC&_nc_sid=86f79a'
b = a.split('?')
print(b[0].split('/')[-1])