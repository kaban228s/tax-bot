from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.notifications import notify_new_user

main_router = Router()

INTROS = {
    'split': ('🎯 Определить признаки разделения бизнеса для ФНС.',
              '📊 Тест покажет, есть ли признаки дробления бизнеса.\nНачнем?'),
    'ausn': ('🎯 Определить, подходит ли вам АУСН.',
             '💡 Тест покажет, выгоден ли переход на АУСН.\nНачнем?'),
    'cash': ('🎯 Проверить операции на соответствие 115-ФЗ.',
             '💸 Тест оценит риски ваших выплат и переводов.\nНачнем?')
}

@main_router.message(CommandStart())
async def cmd_start(msg: Message, state: FSMContext):
    await state.clear()
    await notify_new_user(msg.bot, msg.from_user)
    await msg.answer('👋 Привет!\nЯ — бот Алёны Петрушовой.\nВыберите тест 👇', reply_markup=kb.main)

@main_router.message(F.text == '🟢 Тест на риск дробления бизнеса')
async def m_split(msg: Message, state: FSMContext):
    await start_intro(msg, state, 'split')

@main_router.message(F.text == '🟡 Подходит ли вам УСН или АУСН')
async def m_ausn(msg: Message, state: FSMContext):
    await start_intro(msg, state, 'ausn')

@main_router.message(F.text == '🔵 Легально ли вы выводите наличку')
async def m_cash(msg: Message, state: FSMContext):
    await start_intro(msg, state, 'cash')

async def start_intro(msg: Message, state: FSMContext, test_type: str):
    await state.clear()
    await state.update_data(test_type=test_type, q=0, yes=0)
    goal, intro = INTROS[test_type]
    await msg.answer(goal)
    await msg.answer(intro, reply_markup=kb.start_test)

@main_router.callback_query(F.data == 'decline')
async def decline(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await cb.message.edit_text('Хорошо! Когда будете готовы — выберите тест в меню.')

@main_router.callback_query(F.data == 'back_to_menu')
async def back_menu(cb: CallbackQuery, state: FSMContext):
    await state.clear()
    await cb.answer()
    await cb.message.edit_text('Возвращаемся...')
    await cb.message.answer('Выберите тест 👇', reply_markup=kb.main)

@main_router.callback_query(F.data.startswith('other_'))
async def other(cb: CallbackQuery, state: FSMContext):
    t = cb.data.replace('other_', '')
    await state.clear()
    await state.update_data(test_type=t, q=0, yes=0)
    await cb.answer()
    await cb.message.edit_text(INTROS[t][1], reply_markup=kb.start_test)