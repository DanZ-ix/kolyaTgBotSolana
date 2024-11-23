
import asyncio
import time

import aiohttp
from loader import send_list, logging, bot
from mongodb import mongo_conn

url = "https://frontend-api.pump.fun/coins/"


async def one_token_call(token: str, session: aiohttp.ClientSession, market_cap: int):
    async with session.get(url + token, verify_ssl=False) as response:
        if response.status != 200:
            logging.error(response)  # TODO Добавить сюда логикику чтобы если токен некорректный, то он один раз отправлял об этом сообщение
        else:
            result = await response.json()
            if result['usd_market_cap'] < market_cap:
                for id in send_list:
                    await bot.send_message(id, "Покупаем токен " + token)





async def checker():
    while True:
        start_time = time.time()

        token_list = mongo_conn.token_list
        if len(token_list) == 0:
            await asyncio.sleep(5)
        market_cap = await mongo_conn.get_market_cap()          # Тут тоже можно ускорить
        if market_cap is not None:
            mc = market_cap.get("market_cap")
        else:
            mc = 10
            await mongo_conn.change_market_cap(10)
        async with aiohttp.ClientSession() as session:
            for token in token_list:
                await one_token_call(token, session, market_cap.get("market_cap"))          #TODO  Можно ускорить, если сделать правильные параллельные запросы
                # coroutines = [one_token_call(t, session) for t in token_list]
            # await asyncio.gather(*coroutines)
        iter_time = (time.time() - start_time)
        if iter_time < 1:
            await asyncio.sleep(1 - iter_time)