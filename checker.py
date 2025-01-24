
import asyncio
import time
import requests

import aiohttp
from loader import send_list, logging, bot
from mongodb import mongo_conn

url = "https://t.me/"




async def checker():
    while True:
        start_time = time.time()

        is_list_empty = True

        async for acc in mongo_conn.get_acc_list():
            is_list_empty = False
            try:
                response = requests.get(url + acc.get('acc'))
                if str(response.content).find('<meta name="robots"') != -1:
                    for id in send_list:
                        await bot.send_message(id, "Аккаунт исчез: " + acc.get('acc'))
                        await asyncio.sleep(3)
                        await bot.send_message(id, "Аккаунт исчез: " + acc.get('acc'))
                        await asyncio.sleep(3)
                        await bot.send_message(id, "Аккаунт исчез: " + acc.get('acc'))
                        await mongo_conn.delete_acc(acc.get('acc'))
            except Exception as e:
                logging.error(e)
        if is_list_empty:
            await asyncio.sleep(60)
        else:
            iter_time = (time.time() - start_time)
            if iter_time < 15:
                await asyncio.sleep(15 - iter_time)