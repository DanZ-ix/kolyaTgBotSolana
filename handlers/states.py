from aiogram.fsm.state import State, StatesGroup


class States(StatesGroup):


  DEFAULT_STATE = State()
  ADD_TOKEN_STATE = State()
  DELETE_TOKEN_STATE = State()
  CHANGE_MARKET_CAP_STATE = State()