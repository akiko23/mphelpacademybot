import datetime
import time
import random
import string

from config import bot, db, GROUP_ID, p2p
import markups


async def check_args(args, user_id: int, invited_user_id=0):
    if not 'manager' in args:
        if args == '' or not args.isnumeric():
            return '0'

        if args.isnumeric():
            if int(args) == user_id:
                args = '0'
                return args
            elif db.user_exists(user_id=args) is False:
                args = '0'
                return args
            else:
                args = str(args)
                return args
        else:
            return '0'

    if 'add_manager-kpmwrhnmwbi2ejgi2hbjbknwnrkhrho24' in args:
        if not db.manager_exists(str(user_id)):
            return 'add_manager'
        else:
            return '0'
    else:
        manager_id = args.split('_')[1]
        if str(manager_id) != str(user_id) and manager_id.isnumeric() and not db.user_exists(invited_user_id) \
                and not db.user_exists_in_any_cool_table(str(invited_user_id)):
            return manager_id
        else:
            return '0'


def days_to_seconds(days):
    return days * 24 * 60 * 60


def seconds_to_days(sec):
    return sec / 24 / 60 / 60


def time_sub_day(get_time):
    try:
        time_now = int(time.time())
        middle_time = int(get_time) - time_now

        if middle_time <= 0:
            return False
        else:
            dt = str(datetime.timedelta(seconds=middle_time))
            return dt
    except:
        return False


async def process_sub_month(user_id):
    days = 30
    time_sub = int(time.time() + days_to_seconds(days))

    db.set_user_attr(user_id, 'subtime', time_sub)

    name_for_link = ''.join([random.choice(list(string.ascii_letters)) for _ in range(20)])
    new_link_data = await bot.create_chat_invite_link(chat_id=GROUP_ID, name=name_for_link,
                                                      expire_date=time_sub,
                                                      member_limit=1,
                                                      creates_join_request=False)
    invite_link = dict(new_link_data)['invite_link']
    db.set_user_attr(user_id, 'subLink', invite_link)

    inviter_id = db.get_user_attr(user_id=user_id, column_name='inviter_id')
    if str(inviter_id).isnumeric():
        if db.user_exists_in_any_cool_table(str(inviter_id)):
            old_balance = int(db.get_manager_attr(inviter_id, 'balance'))
            updated_balance = round(
                500 / 100 * int(db.get_manager_attr(inviter_id, 'percent_from_users'))) + old_balance

            db.set_manager_attr(inviter_id, 'balance', updated_balance)
        elif db.user_exists(str(inviter_id)):
            old_balance = int(db.get_user_attr(inviter_id, 'balance'))
            updated_balance = round(
                500 / 100 * int(db.get_user_attr(inviter_id, 'percent_to_user_from_invited_users'))) + old_balance

            db.set_user_attr(str(inviter_id), 'balance', updated_balance)
    try:
        await bot.unban_chat_member(chat_id=GROUP_ID, user_id=user_id)
    except:
        pass
    db.set_user_attr(user_id, 'subStatus', True)
    await bot.send_message(user_id, f'Вам выдана подписка на {days} дней!\n'
                                    f'Ссылка на вступление в канал: {invite_link}',
                           reply_markup=markups.to_main_menu)


async def buy_sub_with_qiwi(call, money):
    comment = f"{call.from_user.id}_{''.join([random.choice(string.ascii_letters) for _ in range(12)])}"
    bill = p2p.bill(amount=money, lifetime=15, comment=comment)

    db.add_check(call.from_user.id, money=money, bill_id=bill.bill_id)
    await bot.send_message(call.from_user.id, f'Вам нужно отправить {money} рублей на наш счет Qiwi\n'
                                              f'Ссылка: {bill.pay_url}\n'
                                              f'Укажите комментарий к оплате: {comment}',
                           reply_markup=markups.qiwi_buy_menu(url=bill.pay_url, bill=bill.bill_id))
