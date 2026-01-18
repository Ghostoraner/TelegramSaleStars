from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from aiocryptopay import AioCryptoPay, Networks
import database as db
import keyboards as kb
from states import Deposit
from config import CRYPTO_BOT_TOKEN

router = Router()
crypto = AioCryptoPay(token=CRYPTO_BOT_TOKEN, network=Networks.MAIN_NET)


@router.message(F.text == "💳 Пополнить баланс")
async def topup_start(message: types.Message, state: FSMContext):
    await state.clear()
    text = (
        "💳 <b>Пополнение баланса (CryptoBot)</b>\n\n"
        "✏️ Введите сумму пополнения в рублях (RUB):\n"
        "<i>Минимальная сумма: 10₽</i>"
    )
    await message.answer(text, parse_mode="HTML", reply_markup=kb.back_to_main)
    await state.set_state(Deposit.amount)


@router.message(Deposit.amount)
async def create_invoice(message: types.Message, state: FSMContext):
    if not message.text.isdigit():
        return await message.answer("⚠️ Пожалуйста, введите целое число!")

    amount = int(message.text)
    if amount < 10:
        return await message.answer("⚠️ Минимальная сумма пополнения — 10₽.")

    # Payload = ID пользователя
    try:
        inv = await crypto.create_invoice(
            asset='USDT',
            amount=amount,
            fiat='RUB',
            currency_type='fiat',
            payload=str(message.from_user.id)
        )

        await state.update_data(inv_id=inv.invoice_id, amount=amount)

        text = (
            "✅ <b>Счет успешно создан!</b>\n\n"
            f"💰 Сумма: <b>{amount}₽</b>\n"
            "⏳ Ссылка действительна 15 минут.\n\n"
            "👇 Нажмите кнопку ниже для оплаты, а затем «Проверить оплату»."
        )
        await message.answer(text, reply_markup=kb.pay_url_kb(inv.bot_invoice_url), parse_mode="HTML")
    except Exception as e:
        await message.answer(f"❌ Ошибка при создании счета: {e}")


@router.callback_query(F.data == "check_p")
async def check_p(callback: types.CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id

    # Ищем оплаченные чеки
    try:
        invoices = await crypto.get_invoices(status='paid')
        found_invoice = None

        if invoices:
            for i in invoices:
                if i.payload == str(user_id):
                    found_invoice = i
                    break

        if found_invoice:
            amount = float(found_invoice.amount) if found_invoice.fiat == 'RUB' else float(
                found_invoice.amount)  # упрощение

            await db.update_balance(user_id, amount)
            await callback.message.edit_text(
                f"✅ <b>Оплата получена!</b>\n\nБаланс пополнен на <code>{amount}₽</code>",
                parse_mode="HTML"
            )
            await state.clear()
        else:
            await callback.answer("⏳ Оплата еще не найдена. Подождите пару минут.", show_alert=True)

    except Exception as e:
        await callback.answer(f"Ошибка проверки: {e}", show_alert=True)