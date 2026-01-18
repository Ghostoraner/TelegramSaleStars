from aiogram import Router, F, types
from aiogram.filters import CommandStart
import database as db
import keyboards as kb
from aiogram.fsm.context import FSMContext

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await db.add_user(message.from_user.id, message.from_user.username)
    text = (
        f"👋 Привет, <b>{message.from_user.first_name}</b>!\n\n"
        "Я бот для быстрой покупки <b>Telegram Stars</b> ⭐️.\n"
        "Выбирай действие в меню ниже 👇"
    )
    await message.answer(text, reply_markup=kb.main_menu, parse_mode="HTML")

@router.message(F.text == "👤 Профиль")
async def show_profile(message: types.Message):
    user_id = message.from_user.id
    u = await db.get_user(user_id)
    stats = await db.get_user_stats(user_id)

    # Обработка None, если заказов еще не было
    total_orders = stats['total_orders'] or 0
    total_stars = stats['total_stars'] or 0
    total_spent = stats['total_spent'] or 0

    text = (
        f"👤 <b>Личный кабинет</b>\n\n"
        f"🆔 ID: <code>{u['user_id']}</code>\n"
        f"👤 Username: @{u['username']}\n"
        f"💳 Баланс: <code>{u['balance']}₽</code>\n\n"
        f"📊 <b>Ваша статистика:</b>\n"
        f"📦 Заказов: <b>{total_orders}</b>\n"
        f"⭐️ Куплено звезд: <b>{total_stars}</b>\n"
        f"💸 Потрачено: <b>{total_spent}₽</b>\n\n"
        f"📅 Регистрация: {u['reg_date']}"
    )
    await message.answer(text, parse_mode="HTML")

@router.message(F.text == "🆘 Поддержка")
async def support(message: types.Message):
    await message.answer(
        "💎 Возникли вопросы? Нажмите кнопку ниже, чтобы связаться с поддержкой:",
        reply_markup=kb.support_kb
    )

@router.message(F.text == "🔙 На главную") # Или "на главное меню" - проверь текст в keyboards.py
@router.message(F.text == "на главное меню")
async def back_to_menu_handler(message: types.Message, state: FSMContext):
    await state.clear() # Очищаем состояния, если пользователь был в процессе покупки
    await message.answer("Вы вернулись в главное меню", reply_markup=kb.main_menu)