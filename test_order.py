#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from telethon import TelegramClient
from config import *
from channel_to_sheets import parse_message_data

async def test_message_order():
    client = TelegramClient('order_session', API_ID, API_HASH)
    await client.start(PHONE)
    
    channel = await client.get_entity(MY_CHANNEL_ID)
    
    plinko_messages = []
    
    print('🔍 Проверяем порядок сообщений Plinko Tap...')
    
    # Собираем все сообщения с Plinko Tap
    async for message in client.iter_messages(channel, limit=1000):
        if message.text and 'Plinko Tap' in message.text:
            data = parse_message_data(message.text)
            plinko_messages.append({
                'date': message.date,
                'type': data['type'],
                'app_name': data['app_name'],
                'text_preview': message.text[:100]
            })
    
    print(f'Найдено {len(plinko_messages)} сообщений:')
    for i, msg in enumerate(plinko_messages):
        print(f'{i+1}. {msg["date"]} - {msg["type"]} - {msg["app_name"]}')
        print(f'   Превью: {msg["text_preview"]}...')
        print()
    
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_message_order()) 