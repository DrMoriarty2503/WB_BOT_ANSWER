import json
from aiogram.filters.callback_data import CallbackData

from aiogram import types, F, Router
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
import wb_api.wb

router = Router()

import database.requests as rq


@router.message(Command("start"))
async def start_handler(message: Message):
    await rq.set_user(message.from_user.id, message.from_user.username)
    await message.answer("Привет! Бот для ответов на отзывы", reply_markup=kb.main)


# @router.message()
# async def message_handler(msg: Message):
#     await msg.answer(f"Твой ID: {msg.from_user.id}")

@router.message(F.text=='Ответы на отзывы')
async def message_handler(message: Message):
    await message.answer("OK!",reply_markup=kb.reviews_nav)

@router.message(F.text=='Настройка ответов')
async def message_handler(message: Message):
    await message.answer(f"Выберите режим для ответа на отзывы с каждым рейтингом ", reply_markup=await kb.choose_mode(message.from_user.id))




from wb_api.wb import fetch_reviews
# from ya_gpt_api.ya_gpt_api import create_answer
# @router.message(F.text == 'Получить отзывы')
# async def get_reviews(message: Message, state: FSMContext):
#     res = await fetch_reviews()
#     for review in res:
#         article = review['артикул']
#         text = review['текст отзыва']
#         rating = review['оценка']
#         template = await rq.get_template(int(message.from_user.id), int(rating), str(article))
#         answer_gpt = await create_answer(text, template)
#         data = json.loads(answer_gpt)
#         answer = data['result']['alternatives'][0]['message']['text']
#         await message.answer(f'Вот информация об отзыве\n Отзыв:{text} \n Ответ: {answer}')



from .keyboards import Pagination

@router.message(F.text == 'Мои шаблоны')
async def get_templates(message: Message):
    templates = await rq.get_templates(int(message.from_user.id))
    if len(templates)!=0:
        await message.answer(f'{templates[0][1]}\n{templates[0][2]}\n{templates[0][3]}\n{templates[0][4]}', reply_markup=await kb.get_paginated_kb(templates, 0))
    else:
        await message.answer('У вас еще нет шаблонов', reply_markup= await kb.get_paginated_kb(templates,0))
@router.callback_query(lambda c: c.data.startswith('pagination:'))
async def template_pagination_callback(callback: CallbackQuery):
    templates = await rq.get_templates(int(callback.from_user.id))
    page = int(callback.data.split(':')[1])  # Извлекаем номер страницы из данных колбека
    await callback.message.edit_text(f'{templates[page][1]}\n{templates[page][2]}\n{templates[page][3]}\n{templates[page][4]}',
                                             reply_markup=await kb.get_paginated_kb(templates, page))


@router.callback_query(lambda c: c.data.startswith('delete:'))
async def template_pagination_callback(callback: CallbackQuery):
    id = int(callback.data.split(':')[1])
    await rq.delete_template(id)
    templates = await rq.get_templates(int(callback.from_user.id))
    if len(templates) != 0:
        await callback.message.edit_text(f'{templates[0][1]}\n{templates[0][2]}\n{templates[0][3]}\n{templates[0][4]}', reply_markup=await kb.get_paginated_kb(templates, 0))
    else:
        await callback.message.edit_text('У вас еще нет шаблонов', reply_markup= await kb.get_paginated_kb(templates,0))


class Reg_Template(StatesGroup):
    template_name = State()
    template_text = State()
    template_rating = State()
    template_product = State()

@router.callback_query(lambda c: c.data.startswith('add'))
async def reg_temp1(callback: CallbackQuery, state: FSMContext):
    await state.set_state(Reg_Template.template_name)
    await callback.message.answer('Введите название шаблона', reply_markup=kb.settings_template)

@router.message(Reg_Template.template_name)
async def reg_temp2(message: Message, state: FSMContext):
    await state.update_data(template_name=message.text)
    await state.set_state(Reg_Template.template_text)
    await message.answer("Введите описание шаблона", reply_markup=kb.settings_template)

@router.message(Reg_Template.template_text)
async def reg_temp3(message: Message, state: FSMContext):
    await state.update_data(template_text=message.text)
    await state.set_state(Reg_Template.template_rating)
    await message.answer('Введите количество звезд или выберите "Для всех ⭐️"', reply_markup=kb.settings_template2)

@router.callback_query(lambda c: c.data == 'all_stars')
async def all_stars_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(template_rating=0, all_stars=True)  # Set all_stars to True and rating to 0
    await state.set_state(Reg_Template.template_product)
    await callback.message.answer('Введите артикул товара или выберите "Для всех товаров"', reply_markup=kb.settings_template3)

@router.message(Reg_Template.template_rating)
async def reg_temp4(message: Message, state: FSMContext):
    await state.update_data(template_rating=int(message.text), all_stars=False)  # Set all_stars to False
    await state.set_state(Reg_Template.template_product)
    await message.answer('Введите артикул товара или выберите "Для всех товаров"', reply_markup=kb.settings_template3)
@router.callback_query(lambda c: c.data.startswith('star:'))
async def star_handler(callback: CallbackQuery, state: FSMContext):
    rating = int(callback.data.split(':')[1])
    await state.update_data(template_rating=rating, all_stars=False)  # Set all_stars to True and rating to 0
    await state.set_state(Reg_Template.template_product)
    await callback.message.answer('Введите артикул товара или выберите "Для всех товаров"', reply_markup=kb.settings_template3)



@router.callback_query(lambda c: c.data == 'all_products')
async def all_products_handler(callback: CallbackQuery, state: FSMContext):
    await state.update_data(template_product='0', all_products=True)  # Set all_products to True and product to '0'
    data = await state.get_data()
    result = await rq.set_template(
        callback.from_user.id,
        data['template_name'],
        data['template_text'],
        data['template_rating'],
        data['template_product'],
        data['all_stars'],
        data['all_products']
    )
    if result is False:
        await callback.message.answer("Вы превысили лимит шаблонов.")
    else:
        await callback.message.answer(f"Шаблон зарегистрирован. \n {data['template_name']}, {data}")

    await state.clear()

@router.message(Reg_Template.template_product)
async def reg_temp_last(message: Message, state: FSMContext):
    await state.update_data(template_product=message.text, all_products=False)  # Set all_products to False
    data = await state.get_data()
    result = await rq.set_template(
        message.from_user.id,
        data['template_name'],
        data['template_text'],
        data['template_rating'],
        data['template_product'],
        data['all_stars'],
        data['all_products']
    )
    if result is False:
        await message.answer("Вы превысили лимит шаблонов.")
    else:
        await message.answer(f"Шаблон зарегистрирован. \n {data['template_name']}, {data}")

    await state.clear()

@router.callback_query(lambda c: c.data == 'back')
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # Clear the state
    await callback.message.answer("Действие отменено. Вы вышли из режима создания шаблона.")


selected_modes = []  # Хранит выбранные режимы

@router.callback_query(lambda c: c.data.startswith('auto:'))
async def auto_mode_callback(callback: CallbackQuery):
    mode_rating = int(callback.data.split(':')[1])
    mode = True
    await rq.modes(callback.from_user.id, mode_rating, mode)

    await callback.message.edit_reply_markup(reply_markup=await kb.choose_mode(callback.from_user.id))

@router.callback_query(lambda c: c.data.startswith('no_auto:'))
async def manual_mode_callback(callback: CallbackQuery):
    mode_rating = int(callback.data.split(':')[1])
    mode = False

    await rq.modes(callback.from_user.id, mode_rating, mode)

    # Обновляем клавиатуру с выбранными режимами
    updated_keyboard = kb.choose_mode(selected_modes)
    await callback.message.edit_reply_markup(reply_markup=await kb.choose_mode(callback.from_user.id))


class Reg_Group(StatesGroup):
    group = State()


@router.message(F.text == 'Группы')
async def reg_group1(message: Message, state: FSMContext):
    await state.set_state(Reg_Group.group)
    await message.answer('Введите группы', reply_markup=kb.settings_group)

@router.message(Reg_Group.group)
async def reg_group2(message: Message, state: FSMContext):
    await state.update_data(group=message.text)
    data = await state.get_data()
    group = data['group']
    await rq.user_groups(message.from_user.id, group)
    await message.answer(f"Группа {group} успешно добавлена")
    await state.clear()

@router.callback_query(lambda c: c.data == 'back_group')
async def cancel_handler(callback: CallbackQuery, state: FSMContext):
    await state.clear()  # Clear the state
    await callback.message.answer("Действие отменено. Вы вышли из режима добавления группы.")


# @router.callback_query(lambda c: c.data.startswith('publicate:'))
# async def process_publicate(callback_query: CallbackQuery):
#     data = callback_query.data.split(':')
#     review_id = data[1]
#     answer = await rq.get_answer(review_id)  # Извлекаем текст ответа
#
#     # Вызываем функцию для публикации ответа
#     await wb_api.wb.publicate_answer(review_id, str(answer))
#     await rq.delete_answer(review_id)
#     await callback_query.message.delete(chat_id=callback_query.message.chat.id, message_id=callback_query.message.message_id)
@router.callback_query(lambda c: c.data.startswith('ignore:'))
async def ignore(callback_query: CallbackQuery):
    review_id = callback_query.data.split(':')[1]
    await rq.delete_answer(review_id)
    await callback_query.message.delete()

@router.callback_query(lambda c: c.data.startswith('get_photo:'))
async def get_photo(callback: CallbackQuery):
    review_id = callback.data.split(':')[1]
    review = await wb_api.wb.get_info_about_review(review_id)

    photo = await wb_api.wb.get_photo_review(review_id)  # Обратите внимание на вызов функции
    if photo:
        await callback.message.answer_photo(photo=photo, caption=f"Вот отзыва для товара {review['data']['productDetails']['nmId']}: {review['data']['productDetails']['productName']}")
    else:
        await callback.message.answer("У данного отзыва нет фото.")

class ChangeAnswer(StatesGroup):
    new_answer = State()
@router.callback_query(lambda c: c.data.startswith('change:'))
async def change_answer(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ChangeAnswer.new_answer)

    data = callback.data.split(':')
    review_id = data[1]
    answer = await rq.get_answer(review_id)
    # Save the review_id in the state
    await state.update_data(review_id=review_id)

    # Set the state to new_answer
    await state.set_state(ChangeAnswer.new_answer)  # Corrected method

    await callback.message.answer(f"{review_id},{answer}, введите новый ответ")
@router.message(ChangeAnswer.new_answer)
async def change_answer2(message: Message, state: FSMContext):
    data = await state.get_data()
    review_id = data.get('review_id')  # Retrieve the saved review_id
    await rq.add_answer(review_id, str(message.text))
    review = await wb_api.wb.get_info_about_review(review_id)
    await state.update_data(new_answer = message.text)  # Set all_products to False
    message_txt = f"Отредактированный ответ на товар:{review['data']['productDetails']['nmId']}\n" \
              f"Пользователь: {review['data']['userName']}\n" \
              f"Оценка: {review['data']['productValuation']}\n" \
              f"Текст: {review['data']['text']}\n" \
              f"Ответ: {message.text}"
    await message.answer(text=message_txt, reply_markup=await kb.get_info_about_review(review_id=review['data']['id']))



    await state.clear()