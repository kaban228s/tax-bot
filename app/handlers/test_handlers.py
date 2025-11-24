from aiogram import F, Router
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import app.keyboards as kb
from app.questions import QUESTIONS
from app.results import get_result_text
from app.states import TestStates
from app.results import RISK_CONFIG, PREPARE_MSGS
test_router = Router()

# Обработчик начала теста — чтобы точно работало при нажатии кнопки "Да, начинаем"
@test_router.callback_query(F.data == 'start_test')
async def start_test_handler(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    # Можно выбирать тест из state или по умолчанию 'split'
    t = data.get('test_type', 'split')
    # Сбрасываем счётчики
    await state.update_data(test_type=t, q=0, yes=0)
    await state.set_state(TestStates.answering)

    first_q = QUESTIONS.get(t, QUESTIONS['split'])[0]
    # если callback был привязан к сообщению — редактируем его; иначе шлём пользователью
    if cb.message:
        await cb.message.edit_text(first_q, reply_markup=kb.boolean)
    else:
        await cb.bot.send_message(cb.from_user.id, first_q, reply_markup=kb.boolean)

    await cb.answer()

# Основной обработчик ответов
@test_router.callback_query(F.data.in_({'yes', 'no'}), TestStates.answering)
async def answer(cb: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    t = data.get('test_type', 'split')
    q = data.get('q', 0)         # индекс текущего вопроса (0-based)
    yes = data.get('yes', 0)

    is_yes = (cb.data == 'yes')
    if is_yes:
        yes += 1

    # --- Спецлогика: для теста 'ausn' — при 'Нет' на первых 3-х вопросах сразу отказ ---
    if t == 'ausn' and q < 3 and not is_yes:
        # Используем конфиг для 'low' уровня
        emoji, title, desc = RISK_CONFIG['ausn']['low']
        prepare = PREPARE_MSGS.get('ausn', '')
        text = (
            f"{emoji} *{title}*\n\n"
            f"{desc}\n\n"
            f"Причина: вы ответили «Нет» на обязательный критерий АУСН (первые 3 вопроса).\n\n"
            f"Что подготовить для проверки:\n{prepare}\n\n"
            "Получите персональный отчёт 👇"
        )

        # Сохраняем состояние (обновляем q/yes, ставим level и переводим стейт)
        await state.update_data(q=q+1, yes=yes, level='low')
        await state.set_state(TestStates.showing_result)

        # Редактируем исходное сообщение, а если его нет — шлём в чат
        if cb.message:
            await cb.message.edit_text(text, reply_markup=kb.get_report, parse_mode='Markdown')
        else:
            await cb.bot.send_message(cb.from_user.id, text, reply_markup=kb.get_report, parse_mode='Markdown')

        await cb.answer()
        return
    # --- /спецлогика ---

    # Обычная логика: двигаем к следующему вопросу или показываем итог
    q += 1
    await state.update_data(q=q, yes=yes)

    if q < len(QUESTIONS[t]):
        next_q = QUESTIONS[t][q]
        if cb.message:
            await cb.message.edit_text(next_q, reply_markup=kb.boolean)
        else:
            await cb.bot.send_message(cb.from_user.id, next_q, reply_markup=kb.boolean)
    else:
        text, level = get_result_text(t, yes)
        await state.update_data(level=level)
        await state.set_state(TestStates.showing_result)
        if cb.message:
            await cb.message.edit_text(text, reply_markup=kb.get_report, parse_mode='Markdown')
        else:
            await cb.bot.send_message(cb.from_user.id, text, reply_markup=kb.get_report, parse_mode='Markdown')

    await cb.answer()