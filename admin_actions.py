import json

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.deep_linking import get_start_link

import markups
from config import bot, dp, db
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ParseMode

from states import AdminStates


async def processing_whole_change_process(call):
    service_name, unique_id = call.data.split('-')[1:]

    if service_name != 'knowlege_baze':
        keyb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Название/Имя',
                                         callback_data=f'chng_param-name-{unique_id}-{service_name}'),
                    InlineKeyboardButton(text='Описание/О себе',
                                         callback_data=f'chng_param-description-{unique_id}-{service_name}')
                ],
                [
                    InlineKeyboardButton(text='Контакт/Ссылку/Имя пользователя',
                                         callback_data=f'chng_param-contact-{unique_id}-{service_name}'),
                ],
                [InlineKeyboardButton(text='Назад', callback_data=f'aftmenu-{service_name}')]
            ]
        )
    else:
        keyb = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(text='Вопрос', callback_data=f'chng_param-name-{unique_id}-{service_name}'),
                    InlineKeyboardButton(text='Ответ',
                                         callback_data=f'chng_param-contact-{unique_id}-{service_name}')
                ],
                [InlineKeyboardButton(text='Назад', callback_data=f'aftmenu-{service_name}')]
            ]
        )
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, 'Выберите, что хотите изменить',
                           reply_markup=keyb)


@dp.callback_query_handler(Text(startswith='chng_param'))
async def change_definite_param(callback: types.CallbackQuery):
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    unique_id, service_name = callback.data.split('-')[2:]

    param_to_change = callback.data.split('-')[1]
    cancel_keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data='quit_process')]
        ]
    )
    res = {"data": [param_to_change, service_name, unique_id]}
    try:
        name, desc, contact = db.get_definite_column_data(service_name, unique_id)[1:]

        with open('current_admin_change_data.json', 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=4, ensure_ascii=False)

        await bot.send_message(callback.from_user.id, f'Введите новое значение\n\n\n'
                                                      f'<b>Текущие данные</b>:\n\n'
                                                      f'<b>Название/Имя</b>: {name}\n'
                                                      f'<b>Описание/О себе</b>: {desc}\n'
                                                      f'<b>Контакт/Ссылка/Имя пользователя</b>: {contact}',
                               reply_markup=cancel_keyb, parse_mode=ParseMode.HTML)
    except ValueError:
        question, answer = db.get_definite_column_data(service_name, unique_id)[1:]

        with open('current_admin_change_data.json', 'w', encoding='utf-8') as f:
            json.dump(res, f, indent=4, ensure_ascii=False)

        await bot.send_message(callback.from_user.id, f'Введите новое значение\n\n\n'
                                                      f'<b>Текущие данные</b>:\n\n'
                                                      f'<b>Вопрос</b>F: {question}\n'
                                                      f'<b>Ответ</b>: {answer}\n',
                               reply_markup=cancel_keyb, parse_mode=ParseMode.HTML)

    await AdminStates.get_value_for_change.set()


@dp.message_handler(content_types=['text'], state=AdminStates.get_value_for_change)
async def get_valueOnChange(msg: types.Message, state: FSMContext):
    await bot.delete_message(msg.from_user.id, msg.message_id - 1)

    with open('current_admin_change_data.json', 'r', encoding='utf-8') as f:
        param_to_change, service_name, unique_id = json.load(f)["data"]

    value = msg.text
    keyb_onFinish = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=f'aftmenu-{service_name}')]
        ]
    )
    db.change_definite_param(service_table=service_name, unique_id=unique_id, column=param_to_change,
                             value=value)
    await bot.send_message(msg.from_user.id, 'Изменения успешно внесены', reply_markup=keyb_onFinish)
    await state.finish()


@dp.callback_query_handler(Text('managers_watch'))
async def watch_managers(call: types.CallbackQuery):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)
    await bot.send_message(call.from_user.id, f'Выберите менеджера.\n'
                                              f'Ссылка для добавления новых менеджеров: {await get_start_link(payload="add_manager-kpmwrhnmwbi2ejgi2hbjbknwnrkhrho24")}',
                           reply_markup=markups.get_managers())
