# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import HtmlResponse
from instaparser.items import InstaparserItem
from instaparser.items import InstaparserFollowItem
import re
import json
from urllib.parse import urlencode
from copy import deepcopy


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://instagram.com/']
    insta_login = '***'
    #Необходимо указывать пароль, который от клиента инсты летит на сервер
    insta_pwd = '***'
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    parse_users = ['booferaxe', 'vixlun']  # Юзеры, у которых собираем посты/подписчиков/подписки

    graphql_url = 'https://www.instagram.com/graphql/query/?'
    posts_hash = '396983faee97f4b49ccbe105b4daf7a0'  # hash для получения данных о постах с главной страницы
    followers_hash = 'c76146de99bb02f6415203be841dd25a'  # hash для получения подписчиков
    following_hash = 'd04b0a864b4b54837c0d870b0e77e076'  # hash для получения подписок

    def parse(self, response: HtmlResponse):  # Логинимся и заходим на главную страницу
        csrf_token = self.fetch_csrf_token(response.text)  # csrf token забираем из html
        yield scrapy.FormRequest(  # заполняем форму для авторизации
            self.inst_login_link,
            method='POST',
            callback=self.user_parse,  # метод который будет обрабатывать полученные значения
            formdata={'username': self.insta_login, 'enc_password': self.insta_pwd},
            headers={'X-CSRFToken': csrf_token})  # передаём csrf токен

    # после авторизации заходим на главную страницу
    def user_parse(self, response: HtmlResponse):
        j_body = json.loads(response.text)  # респонс в джейсон
        if j_body['authenticated']:  # Проверяем на успех авторизации
            for parse_user in self.parse_users:  # Перебираем аккаунты юзеров, у которых собираем инфу
                yield response.follow(
                    # переходим по относительной ссылке
                    f'/{parse_user}',
                    callback=self.user_data_parse,
                    cb_kwargs={'username': parse_user}
                    # явно передаем данные, а не берем из глобального пространства ввиду асинхронщины
                )

    def user_data_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)  # Получаем id пользователя методом fetch_user_id
        variables = {'id': user_id,  # Формируем словарь для передачи даных в запрос
                     'first': 12}  # 12 постов. Можно больше (макс. 50)

        url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'

        # graphql+query_hash: Формируем ссылку для получения .  urlencode кодирует параметры
        url_followers = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
        url_following = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'

        # собираем посты
        yield response.follow(
            url_posts,
            callback=self.user_posts_parse,
            cb_kwargs={'username': username,
                       'user_id': user_id,
                       'variables': deepcopy(variables)})  # variables ч/з deepcopy во избежание изменения основного параметра

        # # собираем подписчиков
        yield response.follow(
            url_followers,
            callback=self.follow_parse,
            cb_kwargs={'username': username,
                        'user_id': user_id,
                        'follow_type': 'follower',
                        'variables': deepcopy(variables),
                        'json_path': 'edge_followed_by'})

        # собираем подпиский
        yield response.follow(
            url_following,
            callback=self.follow_parse,
            cb_kwargs={'username': username,
                       'follow_type': 'following',
                        'user_id': user_id,
                        'variables': deepcopy(variables),
                        'json_path': 'edge_follow'})

    # собираем посты
    def user_posts_parse(self, response: HtmlResponse, username, user_id,
                         variables):  # Принимаем ответ. Не забываем про параметры от cb_kwargs
        j_data = json.loads(response.text)
        # забираем данные у полученного  json
        page_info = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Переходим на след страницу с курсором предыдущий
            url_posts = f'{self.graphql_url}query_hash={self.posts_hash}&{urlencode(variables)}'
            yield response.follow(
                url_posts,
                callback=self.user_posts_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'variables': deepcopy(variables)}
            )
        posts = j_data.get('data').get('user').get('edge_owner_to_timeline_media').get('edges')  # Сами посты
        for post in posts:  # Перебираем посты, собираем данные
            item = InstaparserItem(
                user_id=user_id,
                username=username,
                photo=post['node']['display_url'],
                likes=post['node']['edge_media_preview_like']['count'],
                _id=post['node']['id'],
                post=post['node']  # Закидываем весь ответ сервера, мб будет нужен
            )
            yield item  # В пайплайн

    def follow_parse(self, response: HtmlResponse, username, user_id, variables, follow_type, json_path):
        j_data = json.loads(response.text)
        page_info = j_data.get('data').get('user').get(json_path).get('page_info')
        if page_info.get('has_next_page'):  # Если есть следующая страница
            variables['after'] = page_info['end_cursor']  # Переходим на след страницу с курсором предыдущий
            if follow_type == 'follower':
                url_follow = f'{self.graphql_url}query_hash={self.followers_hash}&{urlencode(variables)}'
            if follow_type == 'following':
                url_follow = f'{self.graphql_url}query_hash={self.following_hash}&{urlencode(variables)}'
            yield response.follow(
                url_follow,
                callback=self.follow_parse,
                cb_kwargs={'username': username,
                           'user_id': user_id,
                           'follow_type': follow_type,
                           'variables': deepcopy(variables),
                           'json_path': json_path})
        follow_users = j_data.get('data').get('user').get(json_path).get('edges')
        for user in follow_users:  # Перебираем подписчиков/подписки
            item = InstaparserFollowItem(
                _id=str(user.get('node').get('id'))+follow_type+str(user_id),
                follow_user_id=user.get('node').get('id'),
                photo_follow=user.get('node').get('profile_pic_url'),
                username_follow=user.get('node').get('username'),
                fullname_follow=user.get('node').get('full_name'),
                username=username,
                follow_type=follow_type
            )
            yield item  # В пайплайн

    # Получаем токен для авторизации
    def fetch_csrf_token(self, text):
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    # Получаем id желаемого пользователя. Т.к. в ответе id не представлен. id нужно вытаскивать из html
    def fetch_user_id(self, text, username):
        matched = re.search(
            '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
        ).group()
        return json.loads(matched).get('id')
