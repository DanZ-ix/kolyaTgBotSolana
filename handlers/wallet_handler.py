import json
import os
import time
import re

from aiogram.filters import Command
from aiogram import types

from loader import dp, kolya_id, logging

admin_list = [kolya_id]

def check_admin(id: int) -> bool:
    return str(id) in admin_list





def add_wallet(wallet_address, blockchain):
    file_path = "watched_wallets.txt"
    with open(file_path, 'a') as f:
        f.write(f'{blockchain}:{wallet_address}\n')


def remove_wallet(wallet_address, blockchain):
    file_path = "watched_wallets.txt"
    temp_file_path = "temp.txt"
    with open(file_path, 'r') as f, open(temp_file_path, 'w') as temp_f:
        for line in f:
            if line.strip() != f'{blockchain}:{wallet_address}':
                temp_f.write(line)
    os.replace(temp_file_path, file_path)


@dp.message(Command('start'))
async def start(message: types.Message):
    if not check_admin(message.from_user.id):
        return
    start_mess = """
👋 Welcome to the Ethereum and Binance Wallet Monitoring Bot!

Use /add <blockchain> <wallet_address> to add a new wallet to monitor.

Example: /add ETH 0x123456789abcdef

Use /remove <blockchain> <wallet_address> to stop monitoring a wallet.

Example: /remove ETH 0x123456789abcdef

Use /list <blockchain> to list all wallets being monitored for a specific blockchain.

Example: /list ETH or just /list
    """

    try:
        await message.answer(start_mess)
    except Exception as e:
        print(e)



@dp.message(Command('add'))
async def add(message: types.Message):
    if not check_admin(message.from_user.id):
        return
    # Получаем текст сообщения
    full_text = message.text
    # Разделяем текст на команду и аргументы
    command, *args = full_text.split()

    if len(args) < 2:
        await message.answer(text="Please provide a blockchain and wallet address to add.")
        return

    blockchain = args[0].lower()
    wallet_address = args[1]

    # Check if the wallet address is in the correct format for the specified blockchain
    if blockchain == 'eth':
        if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
            await message.answer(text=f"{wallet_address} is not a valid Ethereum wallet address.")
            return
    elif blockchain == 'bnb':
        if not re.match(r'^0x[a-fA-F0-9]{40}$', wallet_address):
            await message.answer(text=f"{wallet_address} is not a valid Binance Smart Chain wallet address.")
            return
    else:
        await message.answer(text=f"Invalid blockchain specified: {blockchain}")
        return

    add_wallet(wallet_address, blockchain)
    mess = f'Added {wallet_address} to the list of watched {blockchain.upper()} wallets.'
    await message.answer(text=mess)


@dp.message(Command('remove'))
async def remove(message: types.Message):
    if not check_admin(message.from_user.id):
        return

    full_text = message.text
    # Разделяем текст на команду и аргументы
    command, *args = full_text.split()

    if len(args) < 2:
        await message.answer(text="Please provide a blockchain and wallet address to remove.\nUsage: /remove ETH 0x123456789abcdef")
        return
    blockchain = args[0].lower()
    wallet_address = args[1]
    remove_wallet(wallet_address, blockchain)
    mess = f'Removed {wallet_address} from the list of watched {blockchain.upper()} wallets.'
    await message.answer(text=mess)


@dp.message(Command('list'))
async def list_wallets(message: types.Message):
    if not check_admin(message.from_user.id):
        return
    with open("watched_wallets.txt", "r") as f:
        wallets = [line.strip() for line in f.readlines()]
    if wallets:
        eth_wallets = []
        bnb_wallets = []
        for wallet in wallets:
            blockchain, wallet_address = wallet.split(':')
            if blockchain == 'eth':
                eth_wallets.append(wallet_address)
            elif blockchain == 'bnb':
                bnb_wallets.append(wallet_address)

        mess = "The following wallets are currently being monitored\n"
        mess += "\n"
        if eth_wallets:
            mess += "Ethereum Wallets:\n"
            for i, wallet in enumerate(eth_wallets):
                mess += f"{i + 1}. {wallet}\n"
            mess += "\n"
        if bnb_wallets:
            mess += "Binance Coin Wallets:\n"
            for i, wallet in enumerate(bnb_wallets):
                mess += f"{i + 1}. {wallet}\n"
        await message.answer(text=mess)
    else:
        mess = "There are no wallets currently being monitored."
        await message.answer(text=mess)

