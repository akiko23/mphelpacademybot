import random
import sqlite3
import string
import time


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.Connection(db_file)
        self.cursor = self.connection.cursor()

    def request_to_database(self, request, *args):
        with self.connection:
            return self.cursor.execute(request, *args)

    def add_user(self, user_id):
        self.request_to_database("INSERT INTO users (`user_id`) VALUES (?)", (user_id,))

    def user_exists(self, user_id):
        res = self.request_to_database("SELECT `user_id` FROM users WHERE user_id=?", (user_id,)).fetchall()
        return bool(len(res))

    def get_user_attr(self, user_id, column_name):
        try:
            return self.request_to_database(f"SELECT {column_name} FROM users WHERE user_id=?", (user_id,)).fetchone()[
                0]
        except:
            pass

    def get_manager_attr(self, user_id, column_name):
        return self.request_to_database(f"SELECT {column_name} FROM managers WHERE user_id=?", (user_id,)).fetchone()[0]

    def set_user_attr(self, user_id, column_name, value):
        self.request_to_database(f"UPDATE users SET {column_name}=? WHERE user_id=?", (value, user_id,))

    def get_sub_status(self, user_id):
        sub_time = self.get_user_attr(user_id, 'subtime')
        return True if sub_time > int(time.time()) else False

    def get_admins(self):
        admins = self.request_to_database("SELECT admin_id FROM admins").fetchall()
        return [ad[0] for ad in admins]

    def add_admin(self, user_id):
        self.request_to_database('INSERT INTO admins (admin_id) VALUES (?)', (user_id,))

    def get_definite_service_data(self, service_table):
        return self.request_to_database(f"SELECT * FROM {service_table}").fetchall()

    def reset_manager_money(self, m_id):
        self.request_to_database("UPDATE managers SET balance=? WHERE user_id=?", (0, m_id,))

    def delete_manager(self, m_id):
        self.request_to_database("DELETE FROM managers WHERE user_id=?", (m_id,))

    def get_definite_column_data(self, service_table, unique_id):
        return self.request_to_database(f'SELECT * FROM {service_table} WHERE id=?', (unique_id,)).fetchone()

    def change_definite_param(self, service_table, unique_id, column, value):
        self.request_to_database(f'UPDATE {service_table} SET {column}=? WHERE id=?', (value, unique_id,))

    def set_new_service_item_param(self, service_table, column_name, value, onUpdate=True):
        if onUpdate:
            last_id = self.get_last_column_id(service_table)
            self.request_to_database(f"UPDATE {service_table} SET `{column_name}`=? WHERE `id`=?",
                                     (str(value), last_id,))

        else:
            self.request_to_database(f"INSERT INTO {service_table} (`name`) VALUES (?)", (str(value),))

    def get_last_column_id(self, service_table):
        return self.request_to_database(f'SELECT * FROM {service_table}').fetchall()[-1][0]

    def delete_service_item(self, service_table, unique_id):
        self.request_to_database(f'DELETE FROM {service_table} WHERE id=?', (unique_id,))

    def update_user_money(self, user_id, total_amount):
        full_balance = self.get_user_attr(user_id, 'balance') + total_amount
        return self.request_to_database(f'UPDATE users SET balance=? WHERE user_id=?', (full_balance, user_id,))

    def get_users_with_almost_missed_sub(self):
        cur_time = int(time.time())
        users_with_almost_missed_sub = self.request_to_database(f"SELECT * FROM users WHERE subtime!=0").fetchall()
        return [user[1] for user in users_with_almost_missed_sub if 86400 >= (int(user[4]) - cur_time) >= 0]

    def get_users_with_missed_sub(self):
        cur_time = int(time.time())
        users = self.request_to_database(f"SELECT user_id FROM users WHERE subtime BETWEEN 2 and {cur_time}").fetchall()

        return list(map(lambda x: x[0], users))

    def reset_subscription(self, user_id):
        self.set_user_attr(user_id, 'subtime', 0)

    def get_manager_data(self, user_id):
        return self.request_to_database('SELECT * FROM managers WHERE user_id=?', (user_id,)).fetchone()

    def is_enough_for_buy_sub(self, user_id):
        return self.get_user_attr(user_id, 'balance') >= 500

    def get_managers_param(self, param):
        return [obj[0] for obj in self.request_to_database(f'SELECT {param} FROM managers').fetchall()]

    def set_manager_attr(self, user_id, column_name, value):
        self.request_to_database(f"UPDATE managers SET {column_name}=? WHERE user_id=?", (value, user_id,))

    def get_managers_data(self):
        return self.request_to_database('SELECT * FROM managers').fetchall()

    def get_unreminded_users_after_hour(self):
        all_users_without_sub = self.request_to_database("SELECT * FROM users WHERE subtime=0").fetchall()
        return [user[1] for user in all_users_without_sub if 8200 >= (int(time.time()) - int(user[9])) >= 3600]

    def get_unreminded_users_after_day(self):
        all_users_without_sub = self.request_to_database("SELECT * FROM users WHERE subtime=0").fetchall()
        return [user[1] for user in all_users_without_sub if (int(time.time()) - int(user[9])) >= 86400]

    def update_invited_users(self, table, inviter_id, new_user_id):
        try:
            all_invited_users = self.get_manager_attr(inviter_id, 'invited_users').split(
                ' ') if table == 'managers' else self.get_user_attr(inviter_id, 'invited_users').split(' ')
        except Exception as e:
            all_invited_users = []
        all_invited_users.append(str(new_user_id).strip())

        self.request_to_database(f'UPDATE {table} SET invited_users=? WHERE user_id=?',
                                 (" ".join(list(set(all_invited_users))), inviter_id,))

    def add_manager(self, m_id, m_name, m_ref_link):
        self.request_to_database('INSERT INTO managers (`user_id`, `user_name`, `ref_link`) VALUES (?, ?, ?)',
                                 (m_id, m_name, m_ref_link,))

    def manager_exists(self, user_id):
        res = self.request_to_database("SELECT `user_id` FROM managers WHERE user_id=?", (user_id,)).fetchall()
        return bool(len(res))

    def remove_user(self, user_id):
        self.request_to_database('DELETE FROM users WHERE user_id=?', (user_id,))

    def get_managers_users(self, manager_id, withSub=False):
        if str(manager_id) in self.get_managers_param('user_id'):
            return self.request_to_database('SELECT * FROM users WHERE inviter_id=? and subStatus=true',
                                            (manager_id,)).fetchall() \
                if withSub \
                else self.request_to_database('SELECT * FROM users WHERE inviter_id=?', (manager_id,)).fetchall()

    def user_exists_in_any_cool_table(self, user_id):
        return any([self.manager_exists(user_id), user_id in self.get_admins()])

    def set_all_users_referal_percent(self, percent):
        self.request_to_database("UPDATE users SET percent_to_user_from_invited_users=?", (percent,))

    def add_check(self, user_id, money, bill_id):
        self.request_to_database('INSERT INTO "check" (user_id, money, bill_id) VALUES (?, ?, ?)', (user_id, money, bill_id,))

    def get_check(self, bill_id):
        res = self.request_to_database('SELECT * FROM "check" WHERE bill_id=?', (bill_id,)).fetchmany(1)
        if not bool(len(res)):
            return False
        return res[0]

    def delete_check(self, bill_id):
        self.request_to_database("DELETE FROM 'check' WHERE bill_id=?", (bill_id,))

# db = Database('database.db')
# print(db.get_users_with_almost_missed_sub())
