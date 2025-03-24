
import asyncio
import json
import os
import time
from http.client import responses
from math import floor

import requests

import aiohttp

from configs import TELEGRAM_BOT_TOKEN, ETHERSCAN_API_KEY, BSCSCAN_API_KEY
from loader import send_list, logging, bot, kolya_id
from mongodb import mongo_conn
from uitls import get_links

tg_url = "https://t.me/"
holder_num_filter = 30
bonding_curve_min_percent = 99
min_market_cap = 70000
pumpfun_check_time = 5
token_lifetime_filter = 10 # 10 min


def format_milliseconds_to_text(milliseconds):
    total_seconds = round(milliseconds / 1000)
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    # Формируем строку в зависимости от значений
    if minutes > 0 and seconds > 0:
        return f"{minutes} минут {seconds} секунд"
    elif minutes > 0:
        return f"{minutes} минут"
    else:
        return f"{seconds} секунд"





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

                    if holders_num < holder_num_filter and bonding_curve > bonding_curve_min_percent and token_lifetime < (token_lifetime_filter * 60 * 1000):
                        if mint not in token_list:
                            await mongo_conn.add_new_token(mint)

                            for id in send_list:
                                await bot.send_message(id, f"Токен с mint = {mint} попал под фильтры\n"
                                                           f"Холдеров: {holders_num},\n"
                                                           f"Market cap: {i.get('marketCap')} $\n"
                                                           f"bonding_curve: {bonding_curve}\n"
                                                           f"Прошло времени с момента создания токена: {format_milliseconds_to_text(token_lifetime)}\n\n"
                                                           f"Ссылка: https://pump.fun/coin/{mint}\n"
                                                           f"Адрес dev'а:\n<code>{i.get('dev')}</code>\n"
                                                           f"Адрес СА: \n<code>{mint}</code>\n"
                                                           f"{get_links(mint)}", parse_mode='html', disable_web_page_preview=True)

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

                    if bonding_curve > bonding_curve_min_percent and token_lifetime < (token_lifetime_filter * 60 * 1000):
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
                                                           f"Market cap: {i.get('marketCap')} $\n"
                                                           f"bonding_curve: {bonding_curve}\n"
                                                           f"Прошло времени с момента создания токена: {format_milliseconds_to_text(token_lifetime)}\n\n"
                                                           f"Ссылка: https://pump.fun/coin/{mint}\n"
                                                           f"Адрес dev'а:\n<code>{i.get('dev')}</code>\n"
                                                           f"Адрес СА: \n<code>{mint}</code>\n"
                                                           f"{get_links(mint)}", parse_mode='html', disable_web_page_preview=True)

        except Exception as e:
            logging.error(e)
            print(e)

        iter_time = (time.time() - start_time)
        if iter_time < pumpfun_check_time:
            await asyncio.sleep(pumpfun_check_time - iter_time)



def send_telegram_notification(message, value, usd_value, tx_hash, blockchain):
    if blockchain == 'eth':
        etherscan_link = f'<a href="https://etherscan.io/tx/{tx_hash}">Etherscan</a>'
    elif blockchain == 'bnb':
        etherscan_link = f'<a href="https://bscscan.com/tx/{tx_hash}">BscScan</a>'
    else:
        raise ValueError('Invalid blockchain specified')

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    payload = {'chat_id': f'{kolya_id}', 'text': f'{message}: {etherscan_link}\nValue: {value:.6f} {blockchain.upper()} (${usd_value:.2f})',
               'parse_mode': 'HTML'}
    response = requests.post(url, data=payload)
    logging.error(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Telegram notification sent with message: {message}, value: {value} {blockchain.upper()} (${usd_value:.2f})")
    return response


def get_wallet_transactions(wallet_address, blockchain):
    if blockchain == 'eth':
        url = f'https://api.etherscan.io/api?module=account&action=txlist&address={wallet_address}&sort=desc&apikey={ETHERSCAN_API_KEY}'
    elif blockchain == 'bnb':
        url = f'https://api.bscscan.com/api?module=account&action=txlist&address={wallet_address}&sort=desc&apikey={BSCSCAN_API_KEY}'
    else:
        raise ValueError('Invalid blockchain specified')

    response = requests.get(url)
    data = json.loads(response.text)

    result = data.get('result', [])
    if not isinstance(result, list):
        logging.error(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Error fetching transactions for {wallet_address} on {blockchain.upper()} blockchain: {data}")
        return []

    return result


def monitor_wallets():
    watched_wallets = set()
    file_path = "watched_wallets.txt"
    if not os.path.exists(file_path):
        open(file_path, 'w').close()

    latest_tx_hashes = {}
    latest_tx_hashes_path = "latest_tx_hashes.json"
    if os.path.exists(latest_tx_hashes_path):
        with open(latest_tx_hashes_path, "r") as f:
            latest_tx_hashes = json.load(f)

    last_run_time = 0
    last_run_time_path = "last_run_time.txt"
    if os.path.exists(last_run_time_path):
        with open(last_run_time_path, "r") as f:
            last_run_time = int(f.read())

    while True:
        try:
            print("try")
            # Fetch current ETH and BNB prices in USD from CoinGecko API
            eth_usd_price_url = 'https://api.coingecko.com/api/v3/simple/price?ids=ethereum%2Cbinancecoin&vs_currencies=usd'
            response = requests.get(eth_usd_price_url)
            data = json.loads(response.text)
            eth_usd_price = data['ethereum']['usd']
            bnb_usd_price = data['binancecoin']['usd']

            # Read from file
            with open(file_path, 'r') as f:
                watched_wallets = set(f.read().splitlines())

            for wallet in watched_wallets:
                blockchain, wallet_address = wallet.split(':')
                transactions = get_wallet_transactions(wallet_address, blockchain)
                for tx in transactions:
                    tx_hash = tx['hash']
                    tx_time = int(tx['timeStamp'])

                    if tx_hash not in latest_tx_hashes and tx_time > last_run_time:
                        if tx['to'].lower() == wallet_address.lower():
                            value = float(tx['value']) / 10**18 # Convert from wei to ETH or BNB
                            usd_value = value * (eth_usd_price if blockchain == 'eth' else bnb_usd_price) # Calculate value in USD
                            message = f'🚨 Incoming transaction detected on {wallet_address}'
                            send_telegram_notification(message, value, usd_value, tx['hash'], blockchain)
                            #print(f'\n{message}, Value: {value} {blockchain.upper()}, ${usd_value:.2f}\n')
                        elif tx['from'].lower() == wallet_address.lower():
                            value = float(tx['value']) / 10**18 # Convert from wei to ETH or BNB
                            usd_value = value * (eth_usd_price if blockchain == 'eth' else bnb_usd_price) # Calculate value in USD
                            message = f'🚨 Outgoing transaction detected on {wallet_address}'
                            send_telegram_notification(message, value, usd_value, tx['hash'], blockchain)
                            #print(f'\n{message}, Value: {value} {blockchain.upper()}, ${usd_value:.2f}\n')

                        latest_tx_hashes[tx_hash] = int(tx['blockNumber'])

            # Save latest_tx_hashes to file
            with open(latest_tx_hashes_path, "w") as f:
                json.dump(latest_tx_hashes, f)

            # Update last_run_time
            last_run_time = int(time.time())
            with open(last_run_time_path, "w") as f:
                f.write(str(last_run_time))

            # Sleep for 1 minute
            time.sleep(10)
        except Exception as e:
            print(f'An error occurred: {e}')
            # Sleep for 10 seconds before trying again
            time.sleep(10)
