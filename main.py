import random
import string
import time

import aiogram.types
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text, CommandStart
from aiogram.types import ContentType
from aiogram.utils import executor
from balance_funcs import start_payment_process, get_sum_for_pay

import markups
from aiogram import Dispatcher
from admin_actions import processing_whole_change_process
from config import bot, dp, UKASSA_TOKEN, db, GROUP_ID, SBER_TOKEN, p2p, APP_URL, server, BOT_TOKEN
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.deep_linking import get_start_link

from functions import time_sub_day, days_to_seconds, process_sub_month, buy_sub_with_qiwi
from remind_about_sub_funcs import remind_on_last_days_ofsub, remind_after_hour, remind_after_day
from functions_for_menu import process_get_service
from states import AdminStates
from functions import seconds_to_days, check_args
import os
import logging
from flask import Flask, request


async def always_update_sub_time(msg: types.Message, text, keyb):
    while True:
        await msg.edit_text(text=str(text), reply_markup=keyb)
        time.sleep(2)


@dp.message_handler(CommandStart())
async def start(msg: types.Message):
    user_id = str(msg.from_user.id)
    db.add_user(msg.from_user.id) if not db.user_exists(user_id) and \
                                     not db.user_exists_in_any_cool_table(user_id) else None

    if str(msg.from_user.id) in db.get_managers_param('user_id'):
        ref_link = await get_start_link(payload=f'manager_{msg.from_user.id}')
        db.set_manager_attr(msg.from_user.id, 'ref_link', ref_link)
    else:
        ref_link = await get_start_link(payload=msg.from_user.id)
        db.set_user_attr(msg.from_user.id, 'user_ref_link', ref_link)
        db.set_user_attr(user_id, 'user_date_of_regist', str(round(int(time.time()))))

    args = msg.get_args()
    new_args = await check_args(args, msg.from_user.id)

    db.set_user_attr(msg.from_user.id, 'percent_to_user_from_invited_users',
                     db.get_user_attr('12345', 'percent_to_user_from_invited_users')) \
        if not db.user_exists_in_any_cool_table(msg.from_user.id) \
        else None

    if new_args != '0':
        inviter_id = new_args
        invited_user_id = msg.from_user.id

        if new_args == 'add_manager':
            try:
                db.remove_user(msg.from_user.id)
            except:
                pass
            ref_link = await get_start_link(payload=f'manager_{msg.from_user.id}')
            db.add_manager(msg.from_user.id, msg.from_user.full_name, ref_link)

        else:
            if db.manager_exists(str(inviter_id)):
                db.update_invited_users('managers', inviter_id, str(invited_user_id))
                db.set_manager_attr(inviter_id, 'amount_of_invited_users',
                                    len(db.get_manager_attr(inviter_id, 'invited_users').split(' ')))
            else:
                db.update_invited_users('users', inviter_id, str(invited_user_id))
                db.set_user_attr(inviter_id, 'amount_of_invited_users',
                                 len(db.get_user_attr(inviter_id, 'invited_users').split(' ')))
            db.set_user_attr(invited_user_id, 'inviter_id', inviter_id)

    try:
        menu_keyb = markups.after_subscription_main_menu(msg.from_user.id) if db.get_sub_status(
            msg.from_user.id) or str(
            msg.from_user.id) in db.get_admins() or str(msg.from_user.id) in db.get_managers_param('user_id') \
            else markups.before_subscription_menu(msg.from_user.id)
    except TypeError:
        menu_keyb = markups.after_subscription_main_menu(msg.from_user.id)

    if not db.manager_exists(user_id):
        try:
            time_for_sub = time_sub_day(db.get_user_attr(msg.from_user.id, 'subtime'))
        except:
            time_for_sub = 9999
        user_sub = f"До конца подписки осталось: {time_for_sub}"
        user_sub = 'Подписка не оформлена' if time_for_sub is False else user_sub

        balance = db.get_user_attr(msg.from_user.id, 'balance')

        db.set_user_attr(msg.from_user.id, 'user_date_of_regist', int(time.time())) if not db.user_exists(
            msg.from_user.id) else None

    else:
        user_sub = 'Подписка не требуется'
        balance = db.get_manager_attr(msg.from_user.id, 'balance')

    if str(msg.from_user.id) in db.get_managers_param('user_id'):
        user_ref_link = f"Ваша реферальная ссылка: {db.get_manager_attr(msg.from_user.id, 'ref_link')}"
        href_to_chanel = ''
    else:
        user_ref_link = f"Ваша реферальная ссылка: {db.get_user_attr(msg.from_user.id, 'user_ref_link')}"
        try:
            href = db.get_user_attr(msg.from_user.id, 'subLink')
            href_to_chanel = f"\nОдноразовая ссылка в закрытый канал: {href}" if db.get_sub_status(msg.from_user.id) \
                else ''
        except:
            href_to_chanel = f"\nОдноразовая ссылка не требуется"

    main_photo_id = 'AgACAgIAAxkBAAICzGNY2kZPSsLqObVUgtH7DZwZ8fitAAIlwDEb2ojISpNdWipkecjhAQADAgADcwADKgQ'
    await bot.send_photo(msg.from_user.id, photo=main_photo_id,
                         caption=f"!)Здравствуйте, {msg.from_user.first_name}\n\n"
                                 f"Ваш баланс: {balance} руб.\n"
                                 f"{user_sub}\n"
                                 f"{user_ref_link}"
                                 f"{href_to_chanel}"

                         , reply_markup=menu_keyb)

    unreminded_users_after_hour = db.get_unreminded_users_after_hour()
    unreminded_users_after_day = db.get_unreminded_users_after_day()

    users_with_almost_missed_sub = db.get_users_with_almost_missed_sub()
    users_with_missed_sub = db.get_users_with_missed_sub()

    if any([unreminded_users_after_hour, users_with_almost_missed_sub, users_with_missed_sub,
            unreminded_users_after_day]):
        await remind_on_last_days_ofsub(users_with_almost_missed_sub,
                                        users_with_missed_sub) if unreminded_users_after_day or unreminded_users_after_hour else None
        await remind_after_hour(unreminded_users_after_hour) if unreminded_users_after_hour else None
        await remind_after_day(unreminded_users_after_day) if unreminded_users_after_day else None


@dp.callback_query_handler(Text('sub'))
async def subscription(call: types.CallbackQuery):
    if db.get_sub_status(call.from_user.id) is False:
        try:
            await call.message.edit_caption(
                caption='Подписка открывает доступ к приватной группе, а также к функциям, который на данный момент '
                        'не доступны!\n '
                        '\nЦена подписки - 500 рублей\n'
                        'Будет действовать - 30 дней\n\n',
                reply_markup=markups.onSubpay_menu(call.from_user.id))
        except:
            await call.message.edit_text(
                text='Подписка открывает доступ к приватной группе, а также к функциям, который на данный момент не '
                     'доступны!\n '
                        '\nЦена подписки - 500 рублей\n'
                        'Будет действовать - 30 дней\n\n',
                reply_markup=markups.onSubpay_menu(call.from_user.id))
    else:
        invite_link = db.get_user_attr(call.from_user.id, 'subLink')
        await call.message.edit_caption(caption=f"Подписка уже оформлена. До конца осталось: "
                                                f"{time_sub_day(db.get_user_attr(call.from_user.id, 'subtime'))}\n"
                                                f"Ссылка на вступление в канал: {invite_link}\n"
                                                f"Если желаете продлить подписку, выберите сервис",
                                        reply_markup=markups.onSubpay_menu(call.from_user.id, ukassa=False))


# @dp.callback_query_handler(Text('sub_extend'))
# async def start_extend(call: types.CallbackQuery):
#     await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)
#     await bot.send_message(call.from_user.id, 'Чтобы продлить подписку, нажмите оплатить',
#                            reply_markup=markups.onSubpay_menu(call.from_user.id))


@dp.callback_query_handler(Text(startswith='payservice'))
async def pay_for_sub(call: types.CallbackQuery):
    pay_service = call.data.split('-')[1]
    await bot.delete_message(call.from_user.id, call.message.message_id)

    keyb = InlineKeyboardMarkup()
    keyb.add(InlineKeyboardButton("Заплатить", pay=True))
    keyb.add(InlineKeyboardButton("Отмена", callback_data="to_main_menu"))

    if not 'extend' in call.data:
        if pay_service == 'ukassa':
            await bot.send_invoice(chat_id=call.from_user.id,
                                   title="Оформление подписки",
                                   description="Подписка на приватный канал",
                                   currency='RUB',
                                   payload='month_sub',
                                   provider_token=UKASSA_TOKEN,
                                   start_parameter='test_bot',
                                   reply_markup=keyb,
                                   prices=[{"label": 'Руб', "amount": 50000}])

        elif pay_service == 'self':
            db.update_user_money(call.from_user.id, -500)
            await process_sub_month(call.from_user.id)
        elif pay_service == 'qiwi':
            await buy_sub_with_qiwi(call, money=100)
    else:
        price_for_extend_sub = 500 - 16 * round(
            seconds_to_days(int(db.get_user_attr(call.from_user.id, 'subtime') - time.time())))
        # price_for_extend_sub = 60 if price_for_extend_sub < 60 else price_for_extend_sub
        await buy_sub_with_qiwi(call=call, money=price_for_extend_sub)


@dp.callback_query_handler(Text(contains='check_'))
async def check_qiwi_pay(call: types.CallbackQuery):
    bill = str(call.data[6:])
    info = db.get_check(bill)

    if info is not False:
        if str(p2p.check(bill_id=bill).status) == "PAID":
            await bot.delete_message(call.from_user.id, call.message.message_id)
            await process_sub_month(call.from_user.id)

            db.delete_check(bill_id=bill)
        else:
            await bot.send_message(call.from_user.id, "Вы не оплатили счет",
                                   reply_markup=markups.qiwi_buy_menu(isUrl=False, bill=bill))
    else:
        await bot.send_message(call.from_user.id, 'Счет не найден')


@dp.callback_query_handler(Text(startswith='aftmenu'))
async def menu_buttons(call: types.CallbackQuery):
    service = call.data.split('-')[1]
    await process_get_service(call, service, onBack=True)


@dp.callback_query_handler(Text('set_percent_to_all_users'))
async def set_percent_to_all_users(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, message_id=call.message.message_id)

    current_percent = db.get_user_attr('12345', 'percent_to_user_from_invited_users')
    await bot.send_message(call.from_user.id,
                           f'Введите новый реферальный процент для всех пользователей, кроме менеджеров(числом)\n'
                           f'Текущий процент: {current_percent}',
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [InlineKeyboardButton(text='Отмена', callback_data='q_user_change_percent_process')]
                               ]
                           ))
    await AdminStates.set_percent_to_all_users.set()


@dp.callback_query_handler(Text('q_user_change_percent_process'), state=AdminStates.set_percent_to_all_users)
async def quit_user_change_percent_process(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, 'Вы отменили процесс изменения', reply_markup=markups.to_main_menu)


@dp.message_handler(content_types=['text'], state=AdminStates.set_percent_to_all_users)
async def get_new_users_percent(msg: types.Message, state: FSMContext):
    await bot.delete_message(msg.from_user.id, msg.message_id - 1)
    try:
        new_percent = int(msg.text)
        db.set_all_users_referal_percent(new_percent)

        await bot.send_message(msg.from_user.id, 'Изменения успешно внесены', reply_markup=markups.to_main_menu)
        await state.finish()
    except Exception as e:
        print(e)
        await bot.send_message(msg.from_user.id, 'Отправьте числовое значение')


@dp.callback_query_handler(Text('to_main_menu'))
async def back_to_main_menu(call: types.CallbackQuery):
    if not db.user_exists_in_any_cool_table(str(call.from_user.id)):
        user_sub = f"До конца подписки осталось: {time_sub_day(db.get_user_attr(call.from_user.id, 'subtime'))}"
        user_sub = 'Подписка не оформлена' if time_sub_day(
            db.get_user_attr(call.from_user.id, 'subtime')) is False else user_sub

        balance = db.get_user_attr(call.from_user.id, 'balance')

        db.set_user_attr(call.from_user.id, 'user_date_of_regist', int(time.time())) if not db.user_exists(
            call.from_user.id) else None

    else:
        user_sub = "До конца подписки осталось: 9999999 days"
        try:
            balance = db.get_manager_attr(call.from_user.id, 'balance')
        except:
            balance = 0
    try:
        await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)
    except:
        pass

    if db.manager_exists(str(call.from_user.id)):
        user_ref_link = f"Ваша реферальная ссылка: {db.get_manager_attr(call.from_user.id, 'ref_link')}"
        href_to_chanel = ''
    else:
        user_ref_link = f"Ваша реферальная ссылка: {db.get_user_attr(call.from_user.id, 'user_ref_link')}"
        try:
            href_to_chanel = f"\nОдноразовая ссылка в закрытый канал: {db.get_user_attr(call.from_user.id, 'subLink')}" if db.get_sub_status(
                call.from_user.id) \
                else ''
        except:
            href_to_chanel = f"\nОдноразовая ссылка в закрытый канал не требуется"
    try:
        menu_keyb = markups.after_subscription_main_menu(call.from_user.id) if db.get_sub_status(
            call.from_user.id) or str(
            call.from_user.id) in db.get_admins() or str(call.from_user.id) in db.get_managers_param('user_id') \
            else markups.before_subscription_menu(call.from_user.id)
    except TypeError:
        menu_keyb = markups.after_subscription_main_menu(call.from_user.id)
    main_photo_id = 'AgACAgIAAxkBAAICzGNY2kZPSsLqObVUgtH7DZwZ8fitAAIlwDEb2ojISpNdWipkecjhAQADAgADcwADKgQ'
    await bot.send_photo(call.from_user.id, photo=main_photo_id, caption=f"Ваш баланс: {balance} руб.\n"
                                                                         f"{user_sub}\n"
                                                                         f"{user_ref_link}"
                                                                         f"{href_to_chanel}"
                         , reply_markup=menu_keyb)


@dp.callback_query_handler(Text(startswith='manager'))
async def watch_manager_data(call: types.CallbackQuery):
    manager_id = str(call.data.split('-')[1])
    manager_data = db.get_manager_data(manager_id)

    try:
        users_from_m = len(manager_data[3].split(" "))
    except:
        users_from_m = 0

    try:
        users_with_sub_from_m = len(db.get_managers_users(manager_id, withSub=True))
    except:
        users_with_sub_from_m = 0

    await call.message.edit_text(text=f'Manager data:\n\n'
                                      f'Telegram id: {manager_data[1]}\n'
                                      f'User name: {manager_data[2]}\n\n'
                                      f'Пользователи, начавшие работу с ботом: {users_from_m}\n'
                                      f'Пользователи, купившие подписку: {users_with_sub_from_m}\n\n'
                                      f'Процент выплаты с клиентов: {manager_data[-1]}%\n'
                                      f'Баланс: {manager_data[-2]} RUB',
                                 reply_markup=InlineKeyboardMarkup(
                                     inline_keyboard=[
                                         [InlineKeyboardButton(text='Назад', callback_data='managers_watch')],
                                         [
                                             InlineKeyboardButton(text='Обнулить баланс',
                                                                  callback_data=f'managrs-reset_money-{manager_data[1]}'),
                                             InlineKeyboardButton(text='Удалить менеджера',
                                                                  callback_data=f'managrs-delete-{manager_data[1]}'),
                                         ],
                                         [InlineKeyboardButton(text='Изменить процент по выплатам',
                                                               callback_data=f'chng_managers_percent_from_users-{manager_data[1]}')],
                                         [InlineKeyboardButton(text='В главное меню', callback_data='to_main_menu')]
                                     ]
                                 ))


@dp.callback_query_handler(Text(startswith='managrs'))
async def actions_with_managers(call: types.CallbackQuery):
    action, m_id = call.data.split('-')[1:]
    if action == 'reset_money':
        db.reset_manager_money(m_id)
        await call.message.edit_text(text='Баланс обнуле'
                                          'н', reply_markup=markups.to_main_menu)
    elif action == 'delete':
        db.delete_manager(m_id)
        await call.message.edit_text(text='Удаление прошло успешно', reply_markup=markups.to_main_menu)


@dp.callback_query_handler(Text(startswith='chng_managers_percent_from_users'))
async def change_manager_percent_from_users(call: types.CallbackQuery):
    manager_id = call.data.split('-')[1]
    await call.message.edit_text(text='Введите новое значение(числовое)', reply_markup=InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Отмена', callback_data=f'cancel_change_managers_percent')]
        ]
    ))
    await AdminStates.change_manager_param.set()

    @dp.message_handler(content_types=['text'], state=AdminStates.change_manager_param)
    async def process_change_manager_percent(msg: types.Message, state: FSMContext):
        try:
            await bot.delete_message(msg.from_user.id, msg.message_id - 1)
        except:
            pass
        try:
            new_percent = int(msg.text)

            if new_percent < 0 or new_percent > 100:
                raise ValueError
            db.set_manager_attr(manager_id, 'percent_from_users', new_percent)

            await bot.send_message(msg.from_user.id, 'Изменения успешно внесены', reply_markup=markups.to_main_menu)
            await state.finish()
        except:
            await bot.send_message(msg.from_user.id, 'Неправльный формат', reply_markup=markups.to_main_menu)
            await state.finish()


@dp.callback_query_handler(Text('cancel_change_managers_percent'), state=AdminStates.change_manager_param)
async def cancel_change_managers_percent(call: types.CallbackQuery, state: FSMContext):
    await state.finish()

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, 'Вы отменили процесс изменения', reply_markup=markups.to_main_menu)


@dp.pre_checkout_query_handler()
async def processPreCheckoutQuery(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@dp.message_handler(content_types=ContentType.SUCCESSFUL_PAYMENT)
async def process_pay(msg: types.Message):
    if msg.successful_payment.invoice_payload == "month_sub":
        await process_sub_month(msg.from_user.id)

    elif msg.successful_payment.invoice_payload == 'replenish_balance':
        total_amount = msg.successful_payment.values.get('total_amount') / 100

        db.update_user_money(msg.from_user.id, total_amount)
        await bot.send_message(msg.from_user.id, 'Вы успешно пополнили свой счет!', reply_markup=markups.to_main_menu)


@dp.callback_query_handler(Text(startswith='change'), state=None)
async def menu_buttonsClicksHandler(call: types.CallbackQuery):
    await processing_whole_change_process(call)


@dp.callback_query_handler(Text(startswith='delete'))
async def delete_service_item(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    service_table, unique_id = call.data.split('-')[1:]

    db.delete_service_item(service_table=service_table, unique_id=unique_id)
    await bot.send_message(call.from_user.id, 'Удаление прошло успешно', reply_markup=markups.to_main_menu)


@dp.callback_query_handler(Text('quit_process'), state=AdminStates.all_states)
async def quit_process(call: types.CallbackQuery, state: FSMContext):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await state.finish()

    await bot.send_message(call.from_user.id, 'Вы отменили процесс', reply_markup=markups.to_main_menu)


@dp.callback_query_handler(Text(startswith='add'), state=None)
async def add_item(call: types.CallbackQuery):
    await bot.delete_message(message_id=call.message.message_id, chat_id=call.from_user.id)

    table_name = call.data.split('-')[1]
    name = "Введите название/имя\n" \
           f"Вы сейчас добавляете {table_name}" if table_name != 'knowlege_baze' else "Введите вопрос"

    await bot.send_message(call.from_user.id, name, reply_markup=markups.quit_process_keyb)
    await AdminStates.AddNewItem.get_name.set()

    @dp.message_handler(content_types=['text'], state=AdminStates.AddNewItem.get_name)
    async def set_newItem_name(msg: types.Message):
        await bot.delete_message(message_id=msg.message_id - 1, chat_id=msg.from_user.id)

        item_name = msg.text
        db.set_new_service_item_param(service_table=table_name, column_name='name', value=item_name, onUpdate=False)

        descr = f'Теперь введите описание\n' \
                f'Вы сейчас заполняете {table_name}' if table_name != 'knowlege_baze' else "Введите ответ"

        await bot.send_message(msg.from_user.id, descr, reply_markup=markups.quit_process_keyb)
        await AdminStates.AddNewItem.get_descr.set() if table_name != 'knowlege_baze' \
            else await AdminStates.AddNewItem.get_contact.set()

    @dp.message_handler(content_types=['text'], state=AdminStates.AddNewItem.get_descr)
    async def set_newItem_description(msg: types.Message):
        await bot.delete_message(message_id=msg.message_id - 1, chat_id=msg.from_user.id)

        item_descr = msg.text
        db.set_new_service_item_param(service_table=table_name, column_name='description', value=item_descr)

        await bot.send_message(msg.from_user.id, f'Теперь введите contact\n'
                                                 f'Вы сейчас заполняете {table_name}',
                               reply_markup=markups.quit_process_keyb)
        await AdminStates.AddNewItem.get_contact.set()

    @dp.message_handler(content_types=['text'], state=AdminStates.AddNewItem.get_contact)
    async def set_newItem_contact(msg: types.Message, state: FSMContext):
        await bot.delete_message(message_id=msg.message_id - 1, chat_id=msg.from_user.id)

        item_contact = msg.text
        db.set_new_service_item_param(service_table=table_name, column_name='contact', value=item_contact)

        await bot.send_message(msg.from_user.id, 'Добавление завершено', reply_markup=markups.to_main_menu)
        await state.finish()


@dp.callback_query_handler(Text('put_money'))
async def get_money(call: types.CallbackQuery):
    await start_payment_process(call)


@dp.message_handler(content_types=['text'], state=AdminStates.get_sum_for_payment)
async def replenish_the_balance(msg: types.Message, state: FSMContext):
    await get_sum_for_pay(msg, state)


@dp.message_handler(content_types=['text', 'photo'])
async def path_to_admin(msg: types.Message):
    print(msg)
    if msg.content_type == 'photo':
        with open('photos_services.json', 'a', encoding='utf-8') as f:
            pass

    if msg.text == "}PKQ$EJ(Hqniw-40mofS Fn5w2kjWHDLPPW45H}))":
        await bot.delete_message(msg.from_user.id, msg.message_id)

        db.add_admin(msg.from_user.id)
        await bot.send_message(msg.from_user.id, "Вы успешно стали админом", reply_markup=markups.to_main_menu)


@server.route(f"/{BOT_TOKEN}", methods=["POST"])
def redirect_message(req):
    json_string = req.get_data().decode("utf-8")
    update = aiogram.types.Update.as_json(json_string)
    dp.process_updates([update])
    return ":", 200


def main(func):
    func()


if __name__ == '__main__':
    with db.connection:
        executor.start_polling(dp, skip_updates=True)
