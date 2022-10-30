from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

import markups
from config import db, bot, dp


async def process_get_service(call: types.CallbackQuery, service_name, onBack=False):
    # if not onBack:
    try:
        await bot.delete_message(call.from_user.id, call.message.message_id)
    except:
        pass
    if not 'disabled' in call.data:
        service_data = db.get_definite_service_data(service_name)

        emodzis = {
            'designers': '🌹',
            'fullfiment_services': '📦',
            'knowlege_baze': '📚',
            'ransoms_reviews': '❤️',
            'curators': '👤',
            'buyers': '💰',
            'buhgalters': '🕎',
            'optimization_services': '📈',
            'tables_templates': '📊',
            'news': '📢'
        }
        emodzi = emodzis[service_name]

        services_keyb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text=f"{emodzi}{obj[1]}", callback_data=f'serv-{service_name}-{obj[0]}')]
                for obj in service_data
            ]
        )
        services_keyb.inline_keyboard.append(
            [InlineKeyboardButton(text='Добавить(доступно только админам)', callback_data=f'add-{service_name}')]) \
            if str(call.from_user.id) in db.get_admins() else None

        services_keyb.inline_keyboard.append([InlineKeyboardButton(text='Назад', callback_data='to_main_menu')])

        services_data = {
            'curators': (f'{emodzis["curators"]}КУРАТОРЫ',
                         'AgACAgIAAxkBAAIC3GNY3C0eIi7XifiWRnvFPhjYqRdpAAIqwDEb2ojISoPVPwAB_4oZsgEAAwIAA3MAAyoE'),
            'buhgalters': (f'{emodzis["buhgalters"]}БУХГАЛТЕРЫ',
                           'AgACAgIAAxkBAAIC3WNY3FF5NXmpHxCatHt1usjismryAAIrwDEb2ojISh4PFDQN8lUjAQADAgADcwADKgQ'),
            'designers': (f"{emodzis['designers']}ДИЗАЙНЕРЫ",
                          'AgACAgIAAxkBAAIC5WNY3baWtQPFQ9av5QQEXh8xx_krAAIzwDEb2ojISvZCdyTtO9WnAQADAgADcwADKgQ'),
            'fullfiment_services': (f'{emodzis["fullfiment_services"]}ФУЛФИМЕНТ',
                                    'AgACAgIAAxkBAAIC3mNY3LkeMZjgA2wr8gKoKUEHBEE5AAItwDEb2ojISq1T6lL3Ww2UAQADAgADcwADKgQ'),
            'knowlege_baze': (f'{emodzis["knowlege_baze"]}БАЗА ЗНАНИЙ',
                              'AgACAgIAAxkBAAIC5GNY3ZwUuF2N724rMNTteE1tXxsMAAIywDEb2ojIShnObLqmHdq6AQADAgADcwADKgQ'),
            'ransoms_reviews': (f"{emodzis['ransoms_reviews']}ВЫКУПЫ ОТЗЫВЫ",
                                'AgACAgIAAxkBAAIC5mNY3dN6LuvvsKOKG1vstCkCJsAWAAI0wDEb2ojISltBLqRM7TFfAQADAgADcwADKgQ'),
            'buyers': (f"{emodzis['buyers']}БАЙЕР",
                       'AgACAgIAAxkBAAIC4WNY3SLC3Q7VEShpSz8SVnTOLPlWAAIwwDEb2ojISuro4fdLAsY_AQADAgADcwADKgQ'),
            'optimization_services': (f'{emodzis["optimization_services"]}ОПТИМИЗАЦИЯ',
                                      'AgACAgIAAxkBAAIC4GNY3Qyw0Y3tRhlVngw-eAJDxXmqAAIvwDEb2ojISo5bS803-aWkAQADAgADcwADKgQ'),
            'tables_templates': (f'{emodzis["tables_templates"]}ТАБЛИЦЫ И ШАБЛОНЫ',
                                 'AgACAgIAAxkBAAIC32NY3PQbDoYkHklndyKMkLfXdl0DAAIuwDEb2ojISsX8yRxBl7naAQADAgADcwADKgQ'),
            'news': (f'{emodzis["news"]}НОВОСТИ',
                     'AgACAgIAAxkBAAIC42NY3X00mL8fcsUKIG1_Lj6-3_euAAIxwDEb2ojISsQDRRPz-vvuAQADAgADcwADKgQ')
        }
        name, photo = services_data[service_name]

        # await call.message.edit_caption(caption=f"<b>{name}</b>\n\nСделайте выбор на ваше усмотрение",
        #                                 reply_markup=services_keyb)
        await bot.send_photo(call.from_user.id, photo, caption=f"<b>{name}</b>\n\nСделайте выбор на ваше усмотрение",
                             reply_markup=services_keyb)
    else:
        keyb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text='Купить подписку', callback_data='sub')],
                [InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')],
            ]
        )
        await bot.send_message(call.from_user.id,
                               "Для доступа к функциям данной кнопки, необходимо приобрести подписку",
                               reply_markup=keyb)


@dp.callback_query_handler(Text(startswith='serv'))
async def process_get_name(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    column_id, service_name = callback.data.split('-')[2], callback.data.split('-')[1]
    obj = db.get_definite_column_data(service_table=service_name, unique_id=column_id)

    desc, contact, name = obj[2], obj[-1], obj[1]

    admin_btns = [[InlineKeyboardButton(text="Изменить(доступно только админам)",
                                        callback_data=f'change-{service_name}-{column_id}')],
                  [InlineKeyboardButton(text="Удалить(доступно только админам)",
                                        callback_data=f'delete-{service_name}-{column_id}')
                   ]]

    tables_with_description = ['news', 'tables_templates', 'optimization']

    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Назад', callback_data=f'aftmenu-{service_name}')],
            [InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')]
        ]
    )
    keyb.inline_keyboard.insert(0, [InlineKeyboardButton(text="Написать",
                                                         url=f'https://t.me/{contact}')]) if not service_name in tables_with_description else None
    [keyb.inline_keyboard.append(btn) for btn in admin_btns] if str(user_id) in db.get_admins() else None

    # tables_with_about = ['curators', 'designers', 'ransoms_reviews', 'buhgalters', 'buyer', 'fullfiment']

    if service_name != 'knowlege_baze':
        any_name = 'Название' if service_name in tables_with_description else "Имя"
        any_descr = 'Описание' if service_name in tables_with_description else "О себе"
        any_contact = 'Ссылкa' if service_name in tables_with_description else "Имя пользователя"

        await callback.message.edit_caption(caption=f'{any_name}: {name}\n'
                                                    f'{any_descr}: {desc}\n'
                                                    f'{any_contact}: {contact}',
                                            reply_markup=keyb)

    elif service_name == 'ransoms_reviews':
        any_name, any_descr, any_contact = 'Название', 'О себе', 'Имя пользователя'
        await callback.message.edit_caption(caption=f'{any_name}: {name}\n'
                                                    f'{any_descr}: {desc}\n'
                                                    f'{any_contact}: {contact}',
                                            reply_markup=keyb)
    else:
        keyb.inline_keyboard.pop(0) if keyb.inline_keyboard[0] == [InlineKeyboardButton(text="Написать",
                                                         url=f'https://t.me/{contact}')] else None
        await callback.message.edit_caption(caption=f'Вопрос: {name}\n'
                                                    f'Ответ: {contact}\n',
                                            reply_markup=keyb)
