from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
import app.keyboards as kb
from app.questions import QUESTIONS
from app.results import get_result_text
from app.states import TestStates

test_router = Router()

@test_router.callback_query(F.data == 'start_test')
async def start(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    t = data.get('test_type', 'split')
    await state.update_data(q=0, yes=0)
    await state.set_state(TestStates.answering)
    await cb.answer()
    await cb.message.edit_text(QUESTIONS[t][0], reply_markup=kb.boolean)

@test_router.callback_query(F.data.in_({'yes', 'no'}), TestStates.answering)
async def answer(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    t = data.get('test_type', 'split')
    q = data.get('q', 0)
    yes = data.get('yes', 0)
    
    if cb.data == 'yes':
        yes += 1
    q += 1
    
    await state.update_data(q=q, yes=yes)
    
    if q < len(QUESTIONS[t]):
        await cb.message.edit_text(QUESTIONS[t][q], reply_markup=kb.boolean)
    else:
        text, level = get_result_text(t, yes)
        await state.update_data(level=level)
        await state.set_state(TestStates.showing_result)
        await cb.message.edit_text(text, reply_markup=kb.get_report, parse_mode='Markdown')
    
    await cb.answer()