
from aiogram import types
from handlers import dp
from mongodb import mongo_conn
import asyncio
from checker import checker







async def set_commands(bot):
    await bot.set_my_commands([
        types.BotCommand(command="list_tokens", description="Список отслеживаемых токенов"),
        types.BotCommand(command="add_token", description="Добавить токен"),
        types.BotCommand(command="delete_token", description="Удалить токен"),
        types.BotCommand(command="change_market_cap", description="Изменить маркет кап"),
        types.BotCommand(command="check_market_cap", description="Узнать текущий маркет кап")
    ])


async def main():
    from loader import bot
    await set_commands(bot)
    await mongo_conn.connect_server()

    await asyncio.gather(dp.start_polling(bot), checker())
    print("Бот запущен")

if __name__ == '__main__':
    # asyncio.gather(main(), checker())
    asyncio.run(main())

