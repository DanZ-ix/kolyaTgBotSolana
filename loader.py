from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging

from configs import bot_token

send_list = ["348674843", "1392921102"]
admin_list = send_list



logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger('aiohttp').setLevel(logging.INFO)


bot = Bot(token=bot_token)
dp = Dispatcher(storage=MemoryStorage())
