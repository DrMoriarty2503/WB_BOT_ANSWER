# # тут еще нужно исправить 'isAnswered': True, на False (чтобы получать только неотвеяенные отзывы)
#
# import requests
#
#
# async def fetch_reviews():
#     wb_api_token = 'token'
#     url_all_articles = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
#     headers = {
#         'Authorization': wb_api_token
#     }
#
#     params_all_articles = {
#         "settings": {
#             "cursor": {
#                 "limit": 10
#             },
#             "filter": {
#                 "withPhoto": -1
#             }
#         }
#     }
#
#     all_articles = requests.post(url=url_all_articles, headers=headers, json=params_all_articles)
#     res = all_articles.json()
#     articles = res['cards']
#     all_articles = []
#     all_reviews = []
#     for a in articles:
#         all_articles.append(a['nmID'])
#
#     for article in all_articles:
#         url_all_reviews = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks'
#
#         params_all_reviews = {
#             'isAnswered': True,
#             'nmId': article,
#             'take': 100,
#             'skip': 0,
#
#         }
#
#         res = requests.get(url=url_all_reviews, params=params_all_reviews, headers=headers)
#
#         reviews = res.json()
#         if 'data' in reviews:
#             feedbacks = reviews['data']['feedbacks']
#             for feedback in feedbacks:
#                 id = feedback['id']
#                 text = feedback['text']
#                 userName = feedback['userName']
#                 productValuation = feedback['productValuation']
#                 productName = feedback['productDetails']['productName']
#                 all_reviews.append({'article': article, 'reviews': {'id': id, 'text': text, 'userName': userName,
#                                                                     'productValuation': productValuation, 'productName': productName}})
#     return all_reviews
#
# async def publicate_answer(review_id, answer):
#     wb_api_token = 'token'
#     url_public_answer = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer'
#     headers = {
#         'Authorization': wb_api_token
#     }
#
#     params = {
#         'id': review_id,
#
#         'text': answer
#     }
#
#     pubclic_answer = requests.post(url=url_public_answer, headers=headers, params=params)
# async def get_photo_review(review_id):
#     wb_api_token = 'token'
#     url_public_answer = 'https://feedbacks-api.wildberries.ru/api/v1/feedback'
#     headers = {
#         'Authorization': wb_api_token
#     }
#
#     params = {
#         'id': review_id,
#     }
#
#     try:
#         res = requests.get(url=url_public_answer, headers=headers, params=params)
#         res.raise_for_status()  # Проверка на ошибки HTTP
#         photo = res.json()
#
#         # Проверяем наличие данных
#         if photo and 'data' in photo:
#             # Проверяем наличие photoLinks
#             if 'photoLinks' in photo['data'] and photo['data']['photoLinks']:
#                 return photo['data']['photoLinks'][0]['fullSize']  # Возвращаем первое фото
#             else:
#                 print("Нет данных о photoLinks для данного отзыва.")
#                 return None
#         else:
#             print("Нет данных о фото для данного отзыва.")
#             return None
#     except requests.exceptions.RequestException as e:
#         print(f"Ошибка при запросе к API: {e}")
#         return None
#
# async def get_info_about_review(review_id):
#     wb_api_token = 'token'
#     url_review = 'https://feedbacks-api.wildberries.ru/api/v1/feedback'
#     headers = {
#         'Authorization': wb_api_token
#     }
#
#     params = {
#         'id': review_id,
#
#
#     }
#
#     res = requests.get(url=url_review, headers=headers, params=params)
#     review = res.json()
#     return review
#
#
import aiohttp
import asyncio


async def fetch_reviews():
    wb_api_token = 'token'
    url_all_articles = 'https://content-api.wildberries.ru/content/v2/get/cards/list'
    headers = {
        'Authorization': wb_api_token
    }

    params_all_articles = {
        "settings": {
            "cursor": {
                "limit": 10
            },
            "filter": {
                "withPhoto": -1
            }
        }
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        # Получаем список всех товаров
        async with session.post(url_all_articles, json=params_all_articles) as response:
            res = await response.json()
            articles = res.get('cards', [])
            all_articles = [a['nmID'] for a in articles]

        all_reviews = []

        # Асинхронно собираем отзывы для каждого товара
        async def fetch_reviews_for_article(article):
            url_all_reviews = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks'
            params_all_reviews = {
                'isAnswered': False,  # Изменено на False
                'nmId': article,
                'take': 100,
                'skip': 0,
            }
            async with session.get(url_all_reviews, params=params_all_reviews) as response:
                reviews = await response.json()
                feedbacks = reviews.get('data', {}).get('feedbacks', [])
                return [
                    {
                        'article': article,
                        'reviews': {
                            'id': feedback['id'],
                            'text': feedback['text'],
                            'userName': feedback['userName'],
                            'productValuation': feedback['productValuation'],
                            'productName': feedback['productDetails']['productName']
                        }
                    }
                    for feedback in feedbacks
                ]

        # Запускаем запросы параллельно
        tasks = [fetch_reviews_for_article(article) for article in all_articles]
        results = await asyncio.gather(*tasks)

        # Объединяем все отзывы
        for result in results:
            all_reviews.extend(result)

    return all_reviews


async def publicate_answer(review_id, answer):
    wb_api_token = 'token'
    url_public_answer = 'https://feedbacks-api.wildberries.ru/api/v1/feedbacks/answer'
    headers = {
        'Authorization': wb_api_token
    }

    params = {
        'id': review_id,
        'text': answer
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.post(url_public_answer, params=params) as response:
            return await response.json()


async def get_photo_review(review_id):
    wb_api_token = 'token'
    url_review = 'https://feedbacks-api.wildberries.ru/api/v1/feedback'
    headers = {
        'Authorization': wb_api_token
    }

    params = {
        'id': review_id,
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url_review, params=params) as response:
            photo = await response.json()
            if photo and 'data' in photo:
                if 'photoLinks' in photo['data'] and photo['data']['photoLinks']:
                    return photo['data']['photoLinks'][0]['fullSize']
            return None


async def get_info_about_review(review_id):
    wb_api_token = 'token'
    url_review = 'https://feedbacks-api.wildberries.ru/api/v1/feedback'
    headers = {
        'Authorization': wb_api_token
    }

    params = {
        'id': review_id,
    }

    async with aiohttp.ClientSession(headers=headers) as session:
        async with session.get(url_review, params=params) as response:
            return await response.json()