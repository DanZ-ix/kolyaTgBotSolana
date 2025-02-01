
import asyncio
import json
import time
import requests
from datetime import datetime

import aiohttp
from loader import send_list, logging, bot
from mongodb import mongo_conn

tg_url = "https://t.me/"
holder_num = 12
min_market_cap = 70000
pumpfun_check_time = 10


async def checker_tg():
    while True:
        start_time = time.time()
        is_list_empty = True

        async for acc in mongo_conn.get_acc_list():
            is_list_empty = False
            try:
                response = requests.get(tg_url + acc.get('acc'))
                if str(response.content).find('<meta name="robots"') != -1:
                    for id in send_list:
                        await bot.send_message(id, "Аккаунт Telegram исчез: " + acc.get('acc'))
                        await asyncio.sleep(3)
                        await bot.send_message(id, "Аккаунт Telegram исчез: " + acc.get('acc'))
                        await asyncio.sleep(3)
                        await bot.send_message(id, "Аккаунт Telegram исчез: " + acc.get('acc'))
                        await mongo_conn.delete_acc(acc.get('acc'))
            except Exception as e:
                logging.error(e)
        if is_list_empty:
            await asyncio.sleep(60)
        else:
            iter_time = (time.time() - start_time)
            if iter_time < 15:
                await asyncio.sleep(15 - iter_time)


async def checker_pumpfun():
    while True:
        start_time = time.time()


        try:
            response = requests.get(f"https://advanced-api-v2.pump.fun/coins/list?sortBy=creationTime&marketCapFrom={str(min_market_cap)}&numHoldersFrom={str(holder_num)}&numHoldersTo={str(holder_num)}").json()

            if len(response) != 0:

                token_list = []
                async for acc in mongo_conn.get_token_list():
                    token_list.append(acc.get("token"))

                for i in response:
                    mint = i.get("coinMint")
                    if mint not in token_list:
                        await mongo_conn.add_new_token(mint)

                        for id in send_list:
                            await bot.send_message(id, f"Токен с mint = {mint} попал под фильтры "
                                                       f"(Холдеров: {str(holder_num)}, market cap больше чем: {str(min_market_cap)} $)\n"
                                                       f"Ссылка: https://pump.fun/coin/{mint}\n"
                                                       f"Адрес dev'а:\n<code>{i.get('dev')}</code>", parse_mode='html')

        except Exception as e:
            logging.error(e)

        iter_time = (time.time() - start_time)
        if iter_time < pumpfun_check_time:
            await asyncio.sleep(pumpfun_check_time - iter_time)
