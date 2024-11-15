from aiogram.fsm.context import FSMContext
from aiogram import types
from aiogram.filters import CommandStart, Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from loader import dp, bot, admin_list
from handlers.states import States
from mongodb import mongo_conn



def check_admin(id: int) -> bool:
    return str(id) in admin_list


@dp.message(CommandStart())
async def process_start_command(message: types.Message):
    if check_admin(message.from_user.id):
        await message.answer("Бот для мониторинга токенов")
    else:
        await message.answer("Нет админского доступа")

@dp.message(Command("add_token"))
async def add_token(message: types.Message, state: FSMContext):
    if check_admin(message.from_user.id):
        await message.answer("Напиши токен, который нужно начать отслеживать, введи exit чтобы не добавлять")
        await state.set_state(States.ADD_TOKEN_STATE)


@dp.message(States.ADD_TOKEN_STATE)
async def add_token_int(message: types.Message, state: FSMContext):
    if check_admin(message.from_user.id):
        if message.text.lower() != 'exit':
            await mongo_conn.add_token(message.text)
            await message.answer("Токен добавлен")
        else:
            await message.answer("Токен НЕ добавлен")
        await state.set_state(States.DEFAULT_STATE)


@dp.message(Command("change_market_cap"))
async def change_market_cap(message: types.Message, state: FSMContext):
    if check_admin(message.from_user.id):
        await message.answer("Напиши новый маркет кап (В долларах) для отслеживания, введи exit чтобы выйти из редактирования")
        await state.set_state(States.CHANGE_MARKET_CAP_STATE)


@dp.message(Command("check_market_cap"))
async def check_market_cap(message: types.Message, state: FSMContext):
    if check_admin(message.from_user.id):
        mc = await mongo_conn.get_market_cap()
        await message.answer("Текущий маркет кап: " + str(mc['market_cap']))
        await state.set_state(States.CHANGE_MARKET_CAP_STATE)

@dp.message(States.CHANGE_MARKET_CAP_STATE)
async def change_market_cap_int(message: types.Message, state: FSMContext):
    try:
        if check_admin(message.from_user.id):
            if message.text.lower() != 'exit':
                if message.text.isdigit():
                    mongo_conn.del_market_cap()
                    await mongo_conn.change_market_cap(int(message.text))
                    await message.answer("market cap изменен")
                else:
                    await message.answer("market cap должен быть числом, выход из редактирования")
            else:
                await message.answer("market cap не изменен")
            await state.set_state(States.DEFAULT_STATE)
    except Exception as e:
        print(e)


@dp.message(Command("delete_token"))
async def del_token(message: types.Message, state: FSMContext):
    if check_admin(message.from_user.id):
        k = await get_keyboard_with_tokens()
        await message.answer("Выбери токен, который нужно перестать отслеживать", reply_markup=k)
        await state.set_state(States.DELETE_TOKEN_STATE)

@dp.callback_query(States.DELETE_TOKEN_STATE)
async def callback_data(message: types.CallbackQuery, state: FSMContext):
    try:
        if check_admin(message.from_user.id):
            await mongo_conn.delete_token(message.data)
            await state.set_state(States.DEFAULT_STATE)
            await bot.send_message(str(message.message.chat.id), "Токен был удален")
    except Exception as e:
        print(e)

@dp.message(Command("list_tokens"))
async def list_tokens(message: types.Message, state: FSMContext):
    try:
        if check_admin(message.from_user.id):

            resp = "На данный момент отслеживаются следующие токены: \n"
            async for token in mongo_conn.get_token_list():
                resp += f"{token['token_id']}\n"
            await message.answer(resp)
    except Exception as e:
        print(e)



async def get_keyboard_with_tokens() -> types.InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    async for token in mongo_conn.get_token_list():
        keyboard_builder.button(text=token.get("token_id"), callback_data=token.get("token_id"))
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


