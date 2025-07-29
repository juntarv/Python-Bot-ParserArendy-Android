#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from telethon import TelegramClient
from config import *
from channel_to_sheets import parse_message_data

async def debug_plinko_tap():
    client = TelegramClient('debug_session', API_ID, API_HASH)
    await client.start(PHONE)
    
    channel = await client.get_entity(MY_CHANNEL_ID)
    
    new_app_data = None
    ban_data = None
    
    # Находим оба сообщения Plinko Tap
    async for message in client.iter_messages(channel):
        if message.text and 'Plinko Tap' in message.text:
            data = parse_message_data(message.text)
            
            if data['type'] == 'new_app':
                new_app_data = data
                print(f'✅ Найдено NEW APP сообщение:')
                print(f'   Название: "{data["app_name"]}"')
                print(f'   repr: {repr(data["app_name"])}')
                print(f'   Тип: {data["type"]}')
                print(f'   Бот: {data["bot"]}')
                print()
                
            elif data['type'] == 'ban':
                ban_data = data
                print(f'❌ Найдено BAN сообщение:')
                print(f'   Название: "{data["app_name"]}"')
                print(f'   repr: {repr(data["app_name"])}')
                print(f'   Тип: {data["type"]}')
                print(f'   Бот: {data["bot"]}')
                print()
    
    if new_app_data and ban_data:
        print(f'🔍 ДЕТАЛЬНОЕ СРАВНЕНИЕ:')
        new_name = new_app_data['app_name']
        ban_name = ban_data['app_name']
        
        print(f'NEW: "{new_name}" (len={len(new_name)})')
        print(f'BAN: "{ban_name}" (len={len(ban_name)})')
        print(f'Равны? {new_name == ban_name}')
        print(f'NEW bytes: {new_name.encode("utf-8")}')
        print(f'BAN bytes: {ban_name.encode("utf-8")}')
        
        # Проверим каждый символ
        print(f'\nПосимвольное сравнение:')
        for i, (c1, c2) in enumerate(zip(new_name, ban_name)):
            if c1 != c2:
                print(f'  Позиция {i}: "{c1}" != "{c2}" (ord: {ord(c1)} vs {ord(c2)})')
        
        # Тестируем логику из bots_match
        from channel_to_sheets import bots_match
        print(f'\nbots_match тест:')
        print(f'  new_bot: "{new_app_data["bot"]}"')
        print(f'  ban_bot: "{ban_data["bot"]}"')
        print(f'  bots_match результат: {bots_match(new_app_data["bot"], ban_data["bot"])}')
        
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(debug_plinko_tap()) 