import datetime
import time
import random
import string

from aiogram import types

from config import bot, db, GROUP_ID
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import aiogram
import markups


async def remind_on_last_days_ofsub(msg=''):
    users_with_almost_missed_sub = db.get_users_with_almost_missed_sub()
    users_with_missed_sub = db.get_users_with_missed_sub()

    if len(users_with_missed_sub) > 0:
        for user_id in users_with_missed_sub:
            if not db.get_user_attr(user_id, 'isAlertedAboutFinishSub'):
                try:
                    await bot.kick_chat_member(chat_id=GROUP_ID, user_id=int(user_id))
                except Exception:
                    continue
                try:
                    await bot.send_message(user_id, '‼️Время подписки истекло. Вы были удалены из группы. Желаете '
                                                    'оформить новую?', reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(text='Да, желаю', callback_data="sub_extend"),
                                InlineKeyboardButton(text='Нет, в главное меню', callback_data='to_main_menu')
                            ]
                        ]
                    ))

                except aiogram.exceptions.CantInitiateConversation as e:
                    print(e)
                    pass
                db.reset_subscription(user_id)
                db.set_user_attr(user_id, 'isAlertedAboutFinishSub', True)
            else:
                continue

    if len(users_with_almost_missed_sub) > 0:
        for user_id in users_with_almost_missed_sub:
            if not db.get_user_attr(user_id, 'isAlertedAboutLastSubDay'):
                try:
                    await bot.send_message(user_id, '❗️До конца подписки осталось меньше дня. Желаете '
                                                    'продлить подписку?', reply_markup=InlineKeyboardMarkup(
                        inline_keyboard=[
                            [
                                InlineKeyboardButton(text='Да, желаю', callback_data='sub-extend'),
                                InlineKeyboardButton(text='Нет, в главное меню', callback_data='to_main_menu')
                            ]
                        ]
                    ))
                except aiogram.exceptions.CantInitiateConversation:
                    pass
                db.set_user_attr(user_id, 'isAlertedAboutLastSubDay', True)
            else:
                continue
    else:
        return False


async def remind_after_hour(msg: types.Message):
    unreminded_users = db.get_unreminded_users_after_hour()
    if len(unreminded_users) > 0:
        for user_id in unreminded_users:
            if not db.get_user_attr(user_id, 'is_reminded_after_hour'):
                try:
                    await bot.send_message(user_id,
                                           'Вы недавно заходили в нашего бота, но так и не приобрели подписку. '
                                           'Скажите, желаете ли приобрести подписку?',
                                           reply_markup=InlineKeyboardMarkup(
                                               inline_keyboard=[
                                                   [
                                                       InlineKeyboardButton(text='Да, желаю',
                                                                            callback_data='sub-extend'),
                                                       InlineKeyboardButton(text='Нет, в главное меню',
                                                                            callback_data='to_main_menu')
                                                   ]
                                               ]
                                           ))
                except:
                    pass
                db.set_user_attr(user_id, 'is_reminded_after_hour', True)


async def remind_after_day(msg: types.Message):
    unreminded_users_after_day = db.get_unreminded_users_after_day()
    if unreminded_users_after_day:
        for user_id in unreminded_users_after_day:
            if not db.get_user_attr(user_id, 'is_reminded_after_day'):
                try:
                    await bot.send_message(user_id, 'На днях вы заходили в нашего бота, но так и не приобрели подписку.'
                                                    'Ответьте, желаете ли приобрести подписку?',
                                           reply_markup=InlineKeyboardMarkup(
                                               inline_keyboard=[
                                                   [
                                                       InlineKeyboardButton(text='Да, желаю',
                                                                            callback_data='sub-extend'),
                                                       InlineKeyboardButton(text='Нет, в главное меню',
                                                                            callback_data='to_main_menu')
                                                   ]
                                               ]
                                           ))
                except:
                    pass
                db.set_user_attr(user_id, 'is_reminded_after_day', True)
