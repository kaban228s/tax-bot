from aiogram.fsm.state import State, StatesGroup

class TestStates(StatesGroup):
    answering = State()
    showing_result = State()
    waiting_payment = State()