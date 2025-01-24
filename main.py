
from aiogram import types
from handlers import dp
from mongodb import mongo_conn
import asyncio
from checker import checker


async def set_commands(bot):
    await bot.set_my_commands([
        types.BotCommand(command="list_acc", description="Список отслеживаемых аккаунтов"),
        types.BotCommand(command="add_acc", description="Добавить аккаунт"),
        types.BotCommand(command="delete_acc", description="Удалить аккаунт")
    ])


async def main():
    from loader import bot
    await set_commands(bot)
    await mongo_conn.connect_server()
    await asyncio.gather(dp.start_polling(bot), checker())

    print("Бот запущен")

if __name__ == '__main__':
    asyncio.run(main())
