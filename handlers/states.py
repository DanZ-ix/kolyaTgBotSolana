from aiogram.fsm.state import State, StatesGroup

class States(StatesGroup):
    DEFAULT_STATE = State()
    ADD_TG_ACC_STATE = State()
    DELETE_TG_ACC_STATE = State()
