import requests

##на всякий случай, это ответ для генерации ответа по шаблону
# async def create_answer(review, template):
#     prompt = {
#         "modelUri": "gpt://<ДОСТАЕШЬ ИДЕНТИФИКАТОР ИЗ АДРЕСНОЙ СТРОКИ СЕРВИВИСНОГО АККАУНТА>/yandexgpt-lite",
#         "completionOptions": {
#             "stream": False,
#             "temperature": 0.6,
#             "maxTokens": "2000"
#         },
#         "messages": [
#             {
#                 "role": "system",
#                 "text": "Ты умный бот, который должен отвечать на отзывы клиентов как реальный человек. При этом максимальная длина ответа 40 символов. Твой ответ не должен превышать 40 символов."
#             },
#             {
#                 "role": "user",
#                 "text":f"{review}"
#             },
#             {
#                 "role": "assistant",
#                 "text": f"{template}"
#             },
#
#         ]
#     }
#
#
#     url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
#     headers = {
#         "Content-Type": "application/json",
#         "Authorization": "Api-Key <YOUR API KEY>"
#     }
#
#     response = requests.post(url, headers=headers, json=prompt)
#     result = response.text
#     return result

async def create_answer_to_auto(review, username):
    prompt = {
        "modelUri": "gpt://<ДОСТАЕШЬ ИДЕНТИФИКАТОР ИЗ АДРЕСНОЙ СТРОКИ СЕРВИВИСНОГО АККАУНТА>/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "2000"
        },
        "messages": [
            {
                "role": "system",
                "text": f"Ты умный бот, который должен отвечать на отзывы клиентов как реальный человек. Нужно обращаться к пользователю по его имени {username}"
            },
            {
                "role": "user",
                "text":f"{review}"
            },


        ]
    }


    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key <твой апи ключ, копируешь его из сервисного аккаунта и сразу сохраняешь>"
    }

    response = requests.post(url, headers=headers, json=prompt)
    result = response.text
    return result