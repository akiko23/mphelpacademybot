from aiogram import types

import markups
from config import bot, SBER_TOKEN, UKASSA_TOKEN
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from states import AdminStates


async def start_payment_process(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, 'Введите сумму для пополнения', reply_markup=markups.quit_process_keyb)

    await AdminStates.get_sum_for_payment.set()


async def get_sum_for_pay(msg: types.Message, state):
    await bot.delete_message(msg.from_user.id, msg.message_id - 1)

    try:
        sum_to_pay = int(msg.text)
        print(sum_to_pay * 100)
        if 50000 > sum_to_pay > 5:
            await bot.send_invoice(chat_id=msg.from_user.id,
                                   title="Пополнение баланса",
                                   description=f"Вы собираетесь пополнить ваш баланс на сумму {sum_to_pay} руб.",
                                   currency='RUB',
                                   payload='replenish_balance',
                                   provider_token=UKASSA_TOKEN,
                                   reply_markup=InlineKeyboardMarkup(
                                       inline_keyboard=[
                                           [InlineKeyboardButton(text=f'Заплатить {sum_to_pay} RUB.', pay=True)],
                                           [InlineKeyboardButton(text='Отмена', callback_data='to_main_menu')]
                                       ]
                                   ),
                                   start_parameter='test_bot',
                                   prices=[{"label": 'Руб', "amount": sum_to_pay * 100}])
            await state.finish()
    except Exception as e:
        print(e)
        await bot.send_message(msg.from_user.id, 'Неправильный формат, операция была остановлена', reply_markup=markups.to_main_menu)
        await state.finish()
