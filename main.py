import asyncio
import json
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import app.config
import database.requests
import wb_api.wb
import ya_gpt_api.ya_gpt_api
from app.config import token
from app.handlers import router
import app.keyboards as kb
from database.models import async_main
# from app.handlers import get_reviews
from database.requests import add_answer

###функция распределения отзывово по режимам и дальше уже логика зависит от режима
#####сюда нужно добавить проверку, что пользователь добавил чат, куда будут пересылаться ответы (по умолчанию режим везде ручной)
##### и сюда лучше динамически передавай ид чата (еще обрати внимание, что для автоматиечских ответом и ручных разные чаты)
#####после этого сделай еще одну проверку, что отзывы нашлись (if reviews is not None or len(reviews) != 0) перед циклом по отзывам reviews
async def send_reviews():
    bot = Bot(token=app.config.token)
    while True:
        reviews = await wb_api.wb.fetch_reviews()
        for review in reviews:
            all_modes = await database.requests.get_modes(1082853437)
            for mode in all_modes:
                if int(mode['mode_rating']) == int(review['reviews']['productValuation']):
                    if mode['mode_auto']==True:
                        if str(review['reviews']['text']) != '':
                            ans = await ya_gpt_api.ya_gpt_api.create_answer_to_auto(str(review['reviews']['text']),str(review['reviews']['userName']))
                            answer = json.loads(ans)
                            message = f"Отзыв на товар {review['article']}: {review['reviews']['productName']}\n" \
                                      f"Пользователь: {review['reviews']['userName']}\n" \
                                      f"Оценка: {review['reviews']['productValuation']}\n" \
                                      f"Текст: {review['reviews']['text']}\n" \
                                      f"Ответ: {answer['result']['alternatives'][0]['message']['text']}"
                            await bot.send_message(chat_id='-4772732996', text=message)
                            #     await wb_api.wb.publicate_answer(review_id=review['reviews']['id'],answer=answer)
                            await asyncio.sleep(5)  # Ждем 10 минут

                    if mode['mode_auto']==False:
                        if str(review['reviews']['text']) != '':

                            templates = await database.requests.get_templates(1082853437)
                            print(len(templates))
                            if templates is None or len(templates)==0:
                                ans = await ya_gpt_api.ya_gpt_api.create_answer_to_auto(str(review['reviews']['text']),str(review['reviews']['userName']))
                                answer = json.loads(ans)

                                message = f"Отзыв на товар {review['article']}: {review['reviews']['productName']}\n" \
                                          f"Пользователь: {review['reviews']['userName']}\n" \
                                          f"Оценка: {review['reviews']['productValuation']}\n" \
                                          f"Текст: {review['reviews']['text']}\n" \
                                          f"Ответ: {answer['result']['alternatives'][0]['message']['text']}"
                                await add_answer(review_id = str(review['reviews']['id']),answer=str(answer['result']['alternatives'][0]['message']['text']))
                                await bot.send_message(chat_id='-4775854512', text=message,
                                                       reply_markup=await kb.get_info_about_review(
                                                           review_id=str(review['reviews']['id'])))
                                await asyncio.sleep(5)
                            else:
                                template_found = False  # Flag to check if a template is found

                                for template in templates:
                                    if int(template[4])!=0 and int(template[3]) != 0:
                                        if int(template[4]) == int(review['article']) and int(template[3]) ==int(review['reviews']['productValuation']) :
                                            print('Найден шаблон для данного рейтинга и данного товара')
                                            answer = template[2]
                                            message = f"Отзыв на товар {review['article']}: {review['reviews']['productName']}\n" \
                                                      f"Пользователь: {review['reviews']['userName']}\n" \
                                                      f"Оценка: {review['reviews']['productValuation']}\n" \
                                                      f"Текст: {review['reviews']['text']}\n" \
                                                      f"Ответ: {answer}"
                                            await add_answer(review_id=str(review['reviews']['id']), answer=str(answer))

                                            await bot.send_message(chat_id='-4775854512', text=message, reply_markup=await kb.get_info_about_review(review_id=str(review['reviews']['id'])))
                                            await asyncio.sleep(5)  # Ждем 10 минут
                                            template_found = True
                                            break
                                    if int(template[4])!=0 and int(template[3]) == 0:
                                        if int(template[4]) == int(review['article']):
                                            print('Найден шаблон для всех звезд и данного товара')
                                            answer = template[2]
                                            message = f"Отзыв на товар {review['article']}: {review['reviews']['productName']}\n" \
                                                      f"Пользователь: {review['reviews']['userName']}\n" \
                                                      f"Оценка: {review['reviews']['productValuation']}\n" \
                                                      f"Текст: {review['reviews']['text']}\n" \
                                                      f"Ответ: {answer}"
                                            await add_answer(review_id=str(review['reviews']['id']), answer=str(answer))

                                            await bot.send_message(chat_id='-4775854512', text=message, reply_markup=await kb.get_info_about_review(review_id=str(review['reviews']['id'])))
                                            await asyncio.sleep(5)  # Ждем 10 минут
                                            template_found = True
                                            break
                                    if int(template[4])==0 and int(template[3]) != 0:
                                        if int(template[3]) == int(review['reviews']['productValuation']):
                                            print('Найден шаблон для всех товаров и данной звезды')
                                            answer = template[2]
                                            message = f"Отзыв на товар {review['article']}:: {review['reviews']['productName']}\n" \
                                                      f"Пользователь: {review['reviews']['userName']}\n" \
                                                      f"Оценка: {review['reviews']['productValuation']}\n" \
                                                      f"Текст: {review['reviews']['text']}\n" \
                                                      f"Ответ: {answer}"
                                            await add_answer(review_id=str(review['reviews']['id']), answer=str(answer))

                                            await bot.send_message(chat_id='-4775854512', text=message, reply_markup=await kb.get_info_about_review(review_id=str(review['reviews']['id'])))
                                            await asyncio.sleep(5)  # Ждем 10 минут
                                            template_found = True
                                            break
                                    if int(template[3]) == 0 and int(template[4])==0:
                                        print('Найден шаблон для всех товаров и всех звезд')
                                        answer = template[2]
                                        message = f"Отзыв на товар {review['article']}: {review['reviews']['productName']}\n" \
                                                  f"Пользователь: {review['reviews']['userName']}\n" \
                                                  f"Оценка: {review['reviews']['productValuation']}\n" \
                                                  f"Текст: {review['reviews']['text']}\n" \
                                                  f"Ответ: {answer}"
                                        await add_answer(review_id=str(review['reviews']['id']), answer=str(answer))

                                        await bot.send_message(chat_id='-4775854512', text=message, reply_markup=await kb.get_info_about_review(review_id=str(review['reviews']['id'])))
                                        await asyncio.sleep(5)  # Ждем 10 минут
                                        template_found = True
                                        break



                                if template_found == False:
                                        if str(review['reviews']['text']) != '':
                                            print('Шаблон не найден')

                                            ans = await ya_gpt_api.ya_gpt_api.create_answer_to_auto(str(review['reviews']['text']),str(review['reviews']['userName']))
                                            print(ans)
                                            answer = json.loads(ans)
                                            message = f"Отзыв на товар {review['article']}: {review['reviews']['productName']}\n" \
                                                                  f"Пользователь: {review['reviews']['userName']}\n" \
                                                                  f"Оценка: {review['reviews']['productValuation']}\n" \
                                                                  f"Текст: {review['reviews']['text']}\n" \
                                                                  f"Ответ: {answer['result']['alternatives'][0]['message']['text']}"
                                            await add_answer(review_id=str(review['reviews']['id']), answer=str(
                                                answer['result']['alternatives'][0]['message']['text']))

                                            await bot.send_message(chat_id='-4775854512', text=message,reply_markup=await kb.get_info_about_review(review_id=str(review['reviews']['id'])))
                                            await asyncio.sleep(5)  # Ждем 10 минут





        await asyncio.sleep(60)  # Ждем 10 минут



async def main():
    await async_main()
    bot = Bot(token=app.config.token)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())






if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Создаем задачи для выполнения
    loop = asyncio.get_event_loop()
    loop.create_task(main())  # Запускаем основной бот
    loop.create_task(send_reviews())  # Запускаем отправку отзывов в фоне

    # Запускаем цикл событий
    loop.run_forever()



