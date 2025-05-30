from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import logging

from configs import bot_token

send_list = ["5718363898", "1392921102", "154134326", "7470920094", "59092385"]
admin_list = send_list
kolya_id = "5718363898"


logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger('aiohttp').setLevel(logging.INFO)


bot = Bot(token=bot_token)
dp = Dispatcher(storage=MemoryStorage())
