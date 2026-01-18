from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
import database as db
import keyboards as kb
from states import StarPurchase
from config import STAR_PRICE
from ton_client import send_stars_transaction

router = Router()


@router.message(F.text == "⭐️ Купить звезды")
async def buy_stars_start(message: types.Message):
    text = (
        "⭐️ <b>Покупка Telegram Stars</b>\n\n"
        f"🏷 Актуальный курс: <b>{STAR_PRICE}₽ / 1 шт.</b>\n"
        "⚡️ Автоматическая отправка.\n"
        "🛡 Безопасная сделка.\n\n"
        "Нажмите кнопку ниже, чтобы начать 👇"
    )
    await message.answer(text, reply_markup=kb.buy_stars_inline, parse_mode="HTML")


@router.callback_query(F.data == "start_purchase")
async def ask_count(callback: types.CallbackQuery, state: FSMContext):
    u = await db.get_user(callback.from_user.id)
    max_afford = int(u['balance'] // STAR_PRICE)

    text = (
        "⭐️ <b>Введите количество звезд</b>\n\n"
        f"💰 Ваш баланс: <code>{u['balance']}₽</code>\n"
        f"👉 Доступно для покупки: ~{max_afford} шт.\n\n"
        "📉 <i>Лимиты: от 50 до 10 000 звезд.</i>"
    )
    await callback.message.edit_text(text, reply_markup=kb.back_to_main, parse_mode="HTML")
    await state.set_state(StarPurchase.count)


@router.message(StarPurchase.count)
async def ask_user(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("⚠️ Введите целое число!")

    count = int(message.text)

    if count < 50:
        return await message.answer("⚠️ Минимум можно купить 50 звезд.")
    if count > 10000:
        return await message.answer("⚠️ Максимум за раз — 10 000 звезд.")

    price = round(count * STAR_PRICE, 2)
    await state.update_data(count=count, price=price)

    await message.answer(
        f"✅ Принято: <b>{count} звезд</b>\n"
        f"💵 К оплате: <b>{price}₽</b>\n\n"
        "👤 Теперь отправьте <b>юзернейм</b> (через @) получателя:",
        parse_mode="HTML", reply_markup=kb.back_to_main
    )
    await state.set_state(StarPurchase.username)


@router.message(StarPurchase.username)
async def confirm(message: types.Message, state: FSMContext):
    data = await state.get_data()
    username = message.text.strip()

    # Небольшая очистка юзернейма, если скинули ссылку
    if "t.me/" in username:
        username = username.split("t.me/")[-1].replace("/", "")
    if not username.startswith("@"):
        username = f"@{username}"

    await state.update_data(username=username)

    text = (
        "📝 <b>Подтверждение заказа</b>\n\n"
        f"⭐️ Товар: <b>{data['count']} Telegram Stars</b>\n"
        f"👤 Получатель: <b>{username}</b>\n"
        f"💰 Сумма списания: <b>{data['price']}₽</b>\n\n"
        "Всё верно?"
    )

    await message.answer(text, reply_markup=kb.confirm_order_kb, parse_mode="HTML")


@router.callback_query(F.data == "confirm_final_order")
async def final_step(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    user_id = callback.from_user.id
    u = await db.get_user(user_id)

    # Повторная проверка баланса
    if u['balance'] < data['price']:
        return await callback.answer("❌ Недостаточно средств на балансе!", show_alert=True)

    await callback.message.edit_text("⏳ <b>Обработка транзакции в блокчейне...</b>\nПожалуйста, подождите.",
                                     parse_mode="HTML")

    # Отправка звезд
    success, msg = await send_stars_transaction(data['username'], data['count'])

    if success:
        # Списываем баланс
        await db.update_balance(user_id, -data['price'])
        # Сохраняем в историю заказов
        await db.add_order(user_id, data['count'], data['price'], data['username'])

        await callback.message.edit_text(
            f"✅ <b>Заказ выполнен успешно!</b>\n\n"
            f"⭐️ {data['count']} звезд отправлены пользователю {data['username']}.\n"
            f"Спасибо за покупку!",
            parse_mode="HTML"
        )
    else:
        await callback.message.edit_text(
            f"❌ <b>Ошибка при отправке:</b>\n{msg}\n\n"
            "Свяжитесь с поддержкой.",
            parse_mode="HTML"
        )

    await state.clear()


@router.callback_query(F.data == "to_main")
async def process_to_main(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("🏠 Вы вернулись в главное меню.", reply_markup=kb.main_menu)