
import asyncio
import json
import time
from http.client import responses
from math import floor

import requests

import aiohttp
from loader import send_list, logging, bot
from mongodb import mongo_conn

tg_url = "https://t.me/"
holder_num_filter = 30
bonding_curve_min_percent = 70
min_market_cap = 70000
pumpfun_check_time = 5
token_lifetime_filter = 10 # 10 min

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
            #response = requests.get(f"https://advanced-api-v2.pump.fun/coins/list?sortBy=creationTime&numHoldersTo={str(holder_num_filter)}").json()
            response = requests.get("https://advanced-api-v2.pump.fun/coins/about-to-graduate").json()
            #print(response)
            if len(response) != 0:
                request_current_time = time.time() * 1000
                token_list = []
                async for acc in mongo_conn.get_token_list():
                    token_list.append(acc.get("token"))

                for i in response:

                    mint = i.get("coinMint")
                    token_lifetime = request_current_time - i.get("creationTime")
                    holders_num = int(i.get("numHolders"))
                    bonding_curve = float(i.get("bondingCurveProgress"))

                    if holders_num < holder_num_filter and bonding_curve > bonding_curve_min_percent and token_lifetime < (token_lifetime_filter * 60):
                        if mint not in token_list:
                            await mongo_conn.add_new_token(mint)

                            for id in send_list:
                                await bot.send_message(id, f"Токен с mint = {mint} попал под фильтры\n"
                                                           f"Холдеров: {holders_num},\n"
                                                           f"Market cap: {i.get('marketCap')} $)\n"
                                                           f"bonding_curve: {bonding_curve}\n"
                                                           #f"Прошло времени с момента создания токена (c): {token_lifetime}\n\n"
                                                           f"Ссылка: https://pump.fun/coin/{mint}\n"
                                                           f"Адрес dev'а:\n<code>{i.get('dev')}</code>\n"
                                                           f"Адрес СА: \n<code>{mint}</code>\n", parse_mode='html', disable_web_page_preview=True)

        except Exception as e:
            logging.error(e)
            print(e)

        iter_time = (time.time() - start_time)
        if iter_time < pumpfun_check_time:
            await asyncio.sleep(pumpfun_check_time - iter_time)


async def checker_pumpfun_v2():
    while True:
        start_time = time.time()

        try:
            response = requests.get(f"https://advanced-api-v2.pump.fun/coins/list?sortBy=creationTime&numHoldersTo={str(holder_num_filter)}").json()
            if len(response) != 0:
                request_current_time = time.time() * 1000

                token_list_migrating = []
                for i in response:
                    token_lifetime = request_current_time - i.get("creationTime")
                    holders_num = int(i.get("numHolders"))
                    bonding_curve = float(i.get("bondingCurveProgress"))

                    if bonding_curve > bonding_curve_min_percent and token_lifetime < (token_lifetime_filter * 60):
                        token_list_migrating.append(i)

                if len(token_list_migrating) != 0:
                    token_list = []
                    async for acc in mongo_conn.get_token_list():
                        token_list.append(acc.get("token"))
                    for i in token_list_migrating:
                        mint = i.get("coinMint")
                        token_lifetime = request_current_time - i.get("creationTime")
                        holders_num = int(i.get("numHolders"))
                        bonding_curve = float(i.get("bondingCurveProgress"))

                        if mint not in token_list:
                            await mongo_conn.add_new_token(mint)

                            for id in send_list:
                                await bot.send_message(id, f"Токен с mint = {mint} попал под фильтры(Второй вариант мониторинга)\n"
                                                           f"Холдеров: {holders_num},\n"
                                                           f"Market cap: {i.get('marketCap')} $)\n"
                                                           f"bonding_curve: {bonding_curve}\n"
                                                           f"Прошло времени с момента создания токена (c): {floor(token_lifetime)}\n\n"
                                                           f"Ссылка: https://pump.fun/coin/{mint}\n"
                                                           f"Адрес dev'а:\n<code>{i.get('dev')}</code>\n"
                                                           f"Адрес СА: \n<code>{mint}</code>\n", parse_mode='html', disable_web_page_preview=True)

        except Exception as e:
            logging.error(e)
            print(e)

        iter_time = (time.time() - start_time)
        if iter_time < pumpfun_check_time:
            await asyncio.sleep(pumpfun_check_time - iter_time)



