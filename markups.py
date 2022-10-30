from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import db


def before_subscription_menu(user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='👤Куратор', callback_data='aftmenu-curators')],
            [
                InlineKeyboardButton(text='📈ОПТИМИЗАЦИЯ', callback_data='aftmenu-optimization_services'),
                InlineKeyboardButton(text='🕎БУХГАЛТЕР', callback_data='aftmenu-buhgalters'),
            ],
            [
                InlineKeyboardButton(text='🌹ДИЗАЙНЕР', callback_data='aftmenu-designers_disabled'),
                InlineKeyboardButton(text='💰БАЙЕР', callback_data='aftmenu-buyers_disabled'),
            ],
            [
                InlineKeyboardButton(text='❤️ВЫКУПЫ ОТЗЫВЫ', callback_data='aftmenu-ransoms_reviews_disabled'),
                InlineKeyboardButton(text='📚БАЗА ЗНАНИЙ', callback_data='aftmenu-knowlege_baze_disabled'),
            ],
            [
                InlineKeyboardButton(text='📊ТАБЛИЦЫ ШАБЛОНЫ', callback_data='aftmenu-tables_templates_disabled'),
                InlineKeyboardButton(text='📢НОВОСТИ', callback_data='aftmenu-news_disabled'),
            ],
            [InlineKeyboardButton(text='📦ФУЛФИМЕНТ', callback_data='aftmenu-fullfiment_services')],
            [
                InlineKeyboardButton(text='✅ПОДПИСКА', callback_data='sub'),
                InlineKeyboardButton(text='💵ПОПОЛНИТЬ БАЛАНС', callback_data='put_money')
            ],

        ]
    )


to_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')]
    ]
)


def onSubpay_menu(user_id, ukassa=True):
    call_data = 'payservice_extend' if db.get_sub_status(user_id) else 'payservice'
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Qiwi', callback_data=f'{call_data}-qiwi'),
            ],
            [InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')]
        ]
    )
    keyb.inline_keyboard[0].insert(0, InlineKeyboardButton(text='Юкасса', callback_data=f"{call_data}-ukassa")) if ukassa else None
    if db.is_enough_for_buy_sub(user_id):
        keyb.inline_keyboard.insert(0,
                                    [InlineKeyboardButton(text='Со своего счета', callback_data=f"{call_data}-self")])

    return keyb


def after_subscription_main_menu(user_id):
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='👤Куратор', callback_data='aftmenu-curators')],
            [
                InlineKeyboardButton(text='📈ОПТИМИЗАЦИЯ', callback_data='aftmenu-optimization_services'),
                InlineKeyboardButton(text='🕎БУХГАЛТЕР', callback_data='aftmenu-buhgalters'),
            ],
            [
                InlineKeyboardButton(text='🌹ДИЗАЙНЕР', callback_data='aftmenu-designers'),
                InlineKeyboardButton(text='💰БАЙЕР', callback_data='aftmenu-buyers'),
            ],
            [
                InlineKeyboardButton(text='❤ВЫКУПЫ ОТЗЫВЫ', callback_data='aftmenu-ransoms_reviews'),
                InlineKeyboardButton(text='📚БАЗА ЗНАНИЙ', callback_data='aftmenu-knowlege_baze'),
            ],
            [
                InlineKeyboardButton(text='📊ТАБЛИЦЫ ШАБЛОНЫ', callback_data='aftmenu-tables_templates'),
                InlineKeyboardButton(text='📢НОВОСТИ', callback_data='aftmenu-news'),
            ],
            [InlineKeyboardButton(text='📦ФУЛФИМЕНТ', callback_data='aftmenu-fullfiment_services')],
        ]
    )
    keyb.inline_keyboard.append([
        InlineKeyboardButton(text='✅ПОДПИСКА', callback_data='sub'),
        InlineKeyboardButton(text='💵ПОПОЛНИТЬ БАЛАНС', callback_data='put_money')
    ]) if not str(user_id) in db.get_admins() and not str(user_id) in db.get_managers_param('user_id') else None

    admin_btns = [[InlineKeyboardButton(text='МЕНЕДЖЕРЫ', callback_data='managers_watch')],
                  [InlineKeyboardButton(text='Задать процент всем пользователям', callback_data='set_percent_to_all_users')]]

    [keyb.inline_keyboard.append(admin_btn) for admin_btn in admin_btns] if str(
        user_id) in db.get_admins() else None
    return keyb


def after_subscription_menu():
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Да, желаю', callback_data="sub_extend"),
            ],
            [InlineKeyboardButton(text='Нет, в главное меню', callback_data='to_main_menu')]
        ]
    )
    return keyb


quit_process_keyb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Отмена', callback_data='quit_process')]
    ]
)


def get_managers():
    keyb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=m[2], callback_data=f'manager-{m[1]}')]
            for m in db.get_managers_data()
        ]
    )
    keyb.inline_keyboard.append([InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')])
    return keyb


def qiwi_buy_menu(isUrl=True, url="", bill=""):
    qiwiMenu = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Проверить оплату', callback_data=f"check_{bill}")]
        ]
    )
    qiwiMenu.inline_keyboard.insert(0, [InlineKeyboardButton(text='Ссылка на оплату', url=url)]) if isUrl else None
    return qiwiMenu
