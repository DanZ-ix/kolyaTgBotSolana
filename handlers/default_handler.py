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
        await message.answer("Бот для мониторинга аккаунтов ТГ")
    else:
        await message.answer("Нет админского доступа")

@dp.message(Command("add_acc"))
async def add_token(message: types.Message, state: FSMContext):
    if check_admin(message.from_user.id):
        await message.answer("Напиши acc, который нужно начать отслеживать (без @), введи exit чтобы не добавлять")
        await state.set_state(States.ADD_TOKEN_STATE)


@dp.message(States.ADD_TOKEN_STATE)
async def add_token_int(message: types.Message, state: FSMContext):
    if check_admin(message.from_user.id):
        if message.text.lower() != 'exit':
            await mongo_conn.add_acc(message.text)
            await message.answer("acc добавлен")
        else:
            await message.answer("acc НЕ добавлен")
        await state.set_state(States.DEFAULT_STATE)




@dp.message(Command("delete_acc"))
async def del_token(message: types.Message, state: FSMContext):
    if check_admin(message.from_user.id):
        k = await get_keyboard_with_acc()
        await message.answer("Выбери acc, который нужно перестать отслеживать", reply_markup=k)
        await state.set_state(States.DELETE_TOKEN_STATE)

@dp.callback_query(States.DELETE_TOKEN_STATE)
async def callback_data(message: types.CallbackQuery, state: FSMContext):
    try:
        if check_admin(message.from_user.id):
            await mongo_conn.delete_acc(message.data)
            await state.set_state(States.DEFAULT_STATE)
            await bot.send_message(str(message.message.chat.id), "acc был удален")
    except Exception as e:
        print(e)

@dp.message(Command("list_acc"))
async def list_tokens(message: types.Message, state: FSMContext):
    try:
        if check_admin(message.from_user.id):

            resp = "На данный момент отслеживаются следующие accs: \n"
            async for acc in mongo_conn.get_acc_list():
                resp += f"{acc['acc']}\n"
            await message.answer(resp)
    except Exception as e:
        print(e)



async def get_keyboard_with_acc() -> types.InlineKeyboardMarkup:
    keyboard_builder = InlineKeyboardBuilder()
    async for acc in mongo_conn.get_acc_list():
        keyboard_builder.button(text=acc.get("acc"), callback_data=acc.get("acc"))
    keyboard_builder.adjust(1)
    return keyboard_builder.as_markup()


