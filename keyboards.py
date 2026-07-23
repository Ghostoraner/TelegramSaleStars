from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from config import SUPPORT_USERNAME


main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="⭐️ Купить звезды"), KeyboardButton(text="👤 Профиль")],
    [KeyboardButton(text="💳 Пополнить баланс"), KeyboardButton(text="🆘 Поддержка")]
], resize_keyboard=True, input_field_placeholder="Выберите действие в меню 👇")


buy_stars_inline = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🛍 Оформить заказ", callback_data="start_purchase")],
    [InlineKeyboardButton(text="🔙 На главную", callback_data="to_main")]
])

back_to_main = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отмена", callback_data="to_main")]
])

confirm_order_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data="confirm_final_order")],
    [InlineKeyboardButton(text="❌ Отменить", callback_data="to_main")]
])


def pay_url_kb(url):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Оплатить счет", url=url)],
        [InlineKeyboardButton(text="🔄 Проверить оплату", callback_data="check_p")],
        [InlineKeyboardButton(text="🔙 Отмена", callback_data="to_main")]
    ])

support_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="👨‍💻 Написать админу", url=f"https://t.me/{SUPPORT_USERNAME}")]
])

admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="📊 Статистика бота"), KeyboardButton(text="📢 Рассылка")],
    [KeyboardButton(text="💰 Изменить баланс"), KeyboardButton(text="🔙 На главную")]
], resize_keyboard=True)


admin_cancel = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="❌ Отмена", callback_data="admin_cancel")]
])
