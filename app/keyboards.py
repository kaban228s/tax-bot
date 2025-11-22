from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='🟢 Тест на риск дробления бизнеса')],
    [KeyboardButton(text='🟡 Подходит ли вам УСН или АУСН')],
    [KeyboardButton(text='🔵 Легально ли вы выводите наличку')]
], resize_keyboard=True)

start_test = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да, начинаем", callback_data='start_test')],
    [InlineKeyboardButton(text="Позже", callback_data='decline')]
])

boolean = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Да", callback_data='yes')],
    [InlineKeyboardButton(text="Нет", callback_data='no')]
])

get_report = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📄 Получить отчёт — 390 ₽", callback_data='buy_report')],
    [InlineKeyboardButton(text="🏠 В меню", callback_data='back_to_menu')]
])

get_consult = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="📞 Консультация — 15 000 ₽", callback_data='buy_consult')],
    [InlineKeyboardButton(text="🏠 В меню", callback_data='back_to_menu')]
])

back_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="🏠 В меню", callback_data='back_to_menu')]
])

def other_tests(current):
    btns = []
    if current != 'split':
        btns.append([InlineKeyboardButton(text="🟢 Дробление", callback_data='other_split')])
    if current != 'ausn':
        btns.append([InlineKeyboardButton(text="🟡 УСН/АУСН", callback_data='other_ausn')])
    if current != 'cash':
        btns.append([InlineKeyboardButton(text="🔵 Наличка", callback_data='other_cash')])
    btns.append([InlineKeyboardButton(text="🏠 В меню", callback_data='back_to_menu')])
    return InlineKeyboardMarkup(inline_keyboard=btns)

def payment_kb(url: str, product: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Оплатить", url=url)],
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f'check_{product}')],
        [InlineKeyboardButton(text="❌ Отмена", callback_data='back_to_menu')]
    ])
