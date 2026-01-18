from aiogram.fsm.state import State, StatesGroup

class StarPurchase(StatesGroup):
    count = State()
    username = State()

class Deposit(StatesGroup):
    amount = State()

class AdminState(StatesGroup):
    mailing_text = State()
    change_balance_id = State()
    change_balance_amount = State()