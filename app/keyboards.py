from aiogram.types import ReplyKeyboardMarkup, KeyboardButton,InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.filters.callback_data import CallbackData
from aiogram.utils.keyboard import InlineKeyboardBuilder

import wb_api.wb

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Ответы на отзывы')]
],
    resize_keyboard= True,
    input_field_placeholder='Выберите пункт меню.'
)

reviews_nav = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text = 'Настройка ответов')],
    [KeyboardButton(text = 'Мои шаблоны')],
    [KeyboardButton(text = 'Группы')]
],
    resize_keyboard= True,
    input_field_placeholder='Выберите пункт меню.'
)


async def choose_mode(tg_user_id):
    user_modes = await rq.start_mode(tg_user_id)
    inline_keyboard = []

    for mode in user_modes:
        auto_text = f'Авто {mode['mode_rating']}⭐️'
        manual_text = f'Ручной {mode['mode_rating']}⭐️'
        if mode['mode_auto']==False:
            manual_text += ' ✅'
            auto_text=auto_text
        if mode['mode_auto']==True:
            auto_text += ' ✅'  # Добавляем галочку для выбранного автоматического режима
            manual_text = manual_text

        inline_keyboard.append([
            InlineKeyboardButton(text=auto_text, callback_data=f'auto:{mode['mode_rating']}'),
            InlineKeyboardButton(text=manual_text, callback_data=f'no_auto:{mode['mode_rating']}'),
        ])

    return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)


class Pagination(CallbackData, prefix="pag"):
    page: int


import database.requests as rq
async def get_paginated_kb(templates, page: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Проверка на пустой список шаблонов
    if len(templates) == 0:
        builder.row(InlineKeyboardButton(text='Добавить шаблон', callback_data='add'))
        return builder.as_markup()

    start_offset = page * 1
    end_offset = start_offset + 1

    for template in templates[start_offset:end_offset]:
        builder.row(InlineKeyboardButton(text='Удалить шаблон', callback_data=f'delete:{template[0]}'),
                    InlineKeyboardButton(text='Добавить шаблон', callback_data='add'))

    buttons_row = []
    if page > 0:
        buttons_row.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=f'pagination:{page - 1}',
            )
        )
    if end_offset < len(templates):
        buttons_row.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=f'pagination:{page + 1}',
            )
        )
    builder.row(*buttons_row)
    return builder.as_markup()

settings_template = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data=f'back')]
    ]
)
settings_template2 = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text='1 ⭐️', callback_data='star:1'),
         InlineKeyboardButton(text='2 ⭐️',callback_data='star:2'),
                      InlineKeyboardButton(text='3 ⭐️',callback_data='star:3'),
                      InlineKeyboardButton(text='4 ⭐️',callback_data='star:4'),
                      InlineKeyboardButton(text='5 ⭐️',callback_data='star:5')],


        [InlineKeyboardButton(text='Отмена', callback_data=f'back'),
         InlineKeyboardButton(text='Для всех ⭐️',callback_data='all_stars')]
    ]
)

settings_template3 = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data=f'back'),
         InlineKeyboardButton(text='Для всех товаров',callback_data='all_products')]
    ]
)

settings_group = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data=f'back_group')]
    ]
)


async def get_info_about_review(review_id) -> InlineKeyboardMarkup:
    photo = await wb_api.wb.get_photo_review(review_id)
    if photo:
        inline_keyboard = [
            [InlineKeyboardButton(text='Опубликовать', callback_data=f'publicate:{review_id}'),
             InlineKeyboardButton(text='Редактировать', callback_data=f'change:{review_id}')],
            [InlineKeyboardButton(text='Посмотреть фото', callback_data=f'get_photo:{review_id}')],
            [InlineKeyboardButton(text='Не отвечать', callback_data=f'ignore:{review_id}')],
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    else:
        inline_keyboard = [
            [InlineKeyboardButton(text='Опубликовать', callback_data=f'publicate:{review_id}'),
             InlineKeyboardButton(text='Редактировать', callback_data=f'change:{review_id}')],
            [InlineKeyboardButton(text='Не отвечать', callback_data=f'ignore:{review_id}')],
        ]
        return InlineKeyboardMarkup(inline_keyboard=inline_keyboard)




