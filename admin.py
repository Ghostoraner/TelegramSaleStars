import asyncio
from aiogram import Router, F, types, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
from states import AdminState
from config import ADMIN_ID

router = Router()


# Проверка на админа (фильтр)
def is_admin(message: types.Message):
    return message.from_user.id == ADMIN_ID


@router.message(Command("admin"), is_admin)
async def admin_start(message: types.Message):
    await message.answer("🛠 <b>Добро пожаловать в Админ-панель</b>",
                         reply_markup=kb.admin_menu, parse_mode="HTML")


@router.message(F.text == "📊 Статистика бота", is_admin)
async def admin_stats(message: types.Message):
    count = await db.get_all_users_count()
    stats = await db.get_total_stats()

    rev = stats['revenue'] or 0
    stars = stats['stars'] or 0

    text = (
        "📈 <b>Общая статистика:</b>\n\n"
        f"👥 Всего пользователей: <code>{count}</code>\n"
        f"⭐️ Продано звезд: <code>{stars}</code>\n"
        f"💰 Общая выручка: <code>{rev}₽</code>"
    )
    await message.answer(text, parse_mode="HTML")


# --- Логика Рассылки ---
@router.message(F.text == "📢 Рассылка", is_admin)
async def start_mailing(message: types.Message, state: FSMContext):
    await message.answer("Введите текст рассылки (можно с фото):", reply_markup=kb.admin_cancel)
    await state.set_state(AdminState.mailing_text)


@router.message(AdminState.mailing_text, is_admin)
async def process_mailing(message: types.Message, state: FSMContext, bot: Bot):
    users = await db.get_all_user_ids()
    count = 0
    await message.answer(f"⏳ Начинаю рассылку на {len(users)} пользователей...")

    for user_id in users:
        try:
            await bot.copy_message(chat_id=user_id, from_chat_id=message.chat.id, message_id=message.message_id)
            count += 1
            await asyncio.sleep(0.05)  # Защита от спам-фильтра
        except:
            continue

    await message.answer(f"✅ Рассылка завершена! Получили: {count} чел.")
    await state.clear()


# --- Логика изменения баланса ---
@router.message(F.text == "💰 Изменить баланс", is_admin)
async def admin_change_bal(message: types.Message, state: FSMContext):
    await message.answer("Введите ID пользователя:")
    await state.set_state(AdminState.change_balance_id)


@router.message(AdminState.change_balance_id, is_admin)
async def process_bal_id(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("ID должен быть числом!")
    await state.update_data(target_id=int(message.text))
    await message.answer("Введите новую сумму баланса:")
    await state.set_state(AdminState.change_balance_amount)


@router.message(AdminState.change_balance_amount, is_admin)
async def process_bal_amount(message: types.Message, state: FSMContext):
    data = await state.get_data()
    try:
        new_bal = float(message.text)
        await db.set_user_balance(data['target_id'], new_bal)
        await message.answer(f"✅ Баланс пользователя <code>{data['target_id']}</code> изменен на {new_bal}₽",
                             parse_mode="HTML")
        await state.clear()
    except:
        await message.answer("Ошибка! Введите число.")


@router.callback_query(F.data == "admin_cancel")
async def cancel_admin(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text("Действие отменено.")