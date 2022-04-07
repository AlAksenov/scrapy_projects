#5) Написать запрос к базе, который вернет список подписчиков только указанного пользователя
#6) Написать запрос к базе, который вернет список профилей, на кого подписан указанный пользователь

from pymongo import MongoClient
from pprint import pprint

client = MongoClient('127.0.0.1', 27017)
db = client['instagram']
follow = db.instafollow

followers = follow.find({'username': 'vixlun', 'follow_type': 'follower'})
print('Список подписчиков пользователя vixlun')

for follower in followers:
    pprint(follower)


followings = follow.find({'username': 'vixlun', 'follow_type': 'following'})
print('Список на кого подписан пользователь  vixlun')

for following in followings:
    pprint(following)

