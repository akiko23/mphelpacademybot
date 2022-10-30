from aiogram.dispatcher.filters.state import StatesGroup, State


class AdminStates(StatesGroup):
    get_value_for_change = State()
    get_sum_for_payment = State()

    change_manager_param = State()
    set_percent_to_all_users = State()

    class AddNewItem(StatesGroup):
        get_name = State()
        get_descr = State()
        get_contact = State()
