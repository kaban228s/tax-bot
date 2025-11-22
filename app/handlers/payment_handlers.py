from aiogram import F, Router
from aiogram.types import CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.results import PREPARE_MSGS
from app.states import TestStates
from config import DEBUG_MODE

payment_router = Router()

# Инициализация ЮMoney только если не DEBUG
if not DEBUG_MODE:
    from app.yoo_helper import YooHelper
    from config import YOOMONEY_TOKEN, YOOMONEY_WALLET, YOOMONEY_REDIRECT_URI
    yoo = YooHelper(YOOMONEY_TOKEN, YOOMONEY_WALLET, YOOMONEY_REDIRECT_URI)

PRICES = {'report': 390, 'consult': 15000}


@payment_router.callback_query(F.data == 'buy_report')
async def buy_report(cb: CallbackQuery, state: FSMContext):
    if DEBUG_MODE:
        # В debug режиме сразу отправляем отчёт
        await cb.answer('🛠 DEBUG: Оплата пропущена')
        await send_report(cb, state)
        return
    
    payment = yoo.create_payment(cb.from_user.id, PRICES['report'], "Отчёт")
    
    if not payment:
        await cb.answer('❌ Ошибка создания платежа', show_alert=True)
        return
    
    await state.set_state(TestStates.waiting_payment)
    await state.update_data(payment_id=payment['payment_id'], product='report')
    await cb.answer()
    
    await cb.message.edit_text(
        f'💳 *Оплата отчёта — {PRICES["report"]} ₽*\n\n'
        '1. Нажмите "Оплатить"\n'
        '2. После оплаты нажмите "Я оплатил"',
        parse_mode='Markdown',
        reply_markup=kb.payment_kb(payment['url'], 'report')
    )


@payment_router.callback_query(F.data == 'buy_consult')
async def buy_consult(cb: CallbackQuery, state: FSMContext):
    if DEBUG_MODE:
        await cb.answer('🛠 DEBUG: Оплата пропущена')
        await send_consult_confirm(cb, state)
        return
    
    payment = yoo.create_payment(cb.from_user.id, PRICES['consult'], "Консультация")
    
    if not payment:
        await cb.answer('❌ Ошибка создания платежа', show_alert=True)
        return
    
    await state.set_state(TestStates.waiting_payment)
    await state.update_data(payment_id=payment['payment_id'], product='consult')
    await cb.answer()
    
    await cb.message.edit_text(
        f'💳 *Консультация — {PRICES["consult"]} ₽*\n\n'
        '1. Нажмите "Оплатить"\n'
        '2. После оплаты нажмите "Я оплатил"',
        parse_mode='Markdown',
        reply_markup=kb.payment_kb(payment['url'], 'consult')
    )


@payment_router.callback_query(F.data == 'check_report', TestStates.waiting_payment)
async def check_report(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment_id = data.get('payment_id')
    
    if not payment_id:
        await cb.answer('❌ Платёж не найден', show_alert=True)
        return
    
    await cb.answer('⏳ Проверяем оплату...')
    result = await yoo.check_payment(payment_id)
    
    if result['status']:
        await send_report(cb, state)
    else:
        await cb.message.answer('❌ Оплата пока не найдена.\nПодождите 1-2 минуты.')


@payment_router.callback_query(F.data == 'check_consult', TestStates.waiting_payment)
async def check_consult(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    payment_id = data.get('payment_id')
    
    if not payment_id:
        await cb.answer('❌ Платёж не найден', show_alert=True)
        return
    
    await cb.answer('⏳ Проверяем оплату...')
    result = await yoo.check_payment(payment_id)
    
    if result['status']:
        await send_consult_confirm(cb, state)
    else:
        await cb.message.answer('❌ Оплата пока не найдена.\nПодождите 1-2 минуты.')


async def send_report(cb: CallbackQuery, state: FSMContext):
    import os
    
    data = await state.get_data()
    t = data.get('test_type', 'split')
    level = data.get('level', 'medium')
    
    filename = f"{t}_{level}.pdf"
    filepath = os.path.join("reports", filename)
    
    # Проверяем существование файла ДО отправки
    if not os.path.exists(filepath):
        await cb.message.answer(
            f'⚠️ Файл отчёта не найден!\n\n'
            f'Ожидается: `{filepath}`\n'
            f'Текущая папка: `{os.getcwd()}`\n\n'
            f'Создайте папку reports/ и добавьте PDF-файлы.',
            parse_mode='Markdown'
        )
        return
    
    if os.path.getsize(filepath) == 0:
        await cb.message.answer('⚠️ Файл отчёта пустой! Добавьте реальный PDF.')
        return
    
    await cb.message.answer('✅ Оплата получена! Ваш отчёт 👇')
    
    try:
        await cb.message.answer_document(FSInputFile(filepath))
    except Exception as e:
        await cb.message.answer(f'⚠️ Не удалось отправить файл. Обратитесь к администратору.')
    
    await state.set_state(TestStates.showing_result)
    await cb.message.answer(
        '💡 Хотите разобраться детальнее?\n\n'
        '📍 60 мин онлайн-консультации\n'
        '💰 15 000 ₽',
        reply_markup=kb.get_consult
    )


async def send_consult_confirm(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    t = data.get('test_type', 'split')
    
    await state.clear()
    
    await cb.message.answer('✅ Спасибо! Ассистент свяжется в течение 24 часов.')
    await cb.message.answer(f'📋 *Что подготовить:*\n{PREPARE_MSGS.get(t, "")}', parse_mode='Markdown')
    await cb.message.answer('Хотите пройти другой тест?', reply_markup=kb.other_tests(t))