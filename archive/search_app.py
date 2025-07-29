#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from telethon import TelegramClient
from config import *
import sys

async def search_app(app_name):
    client = TelegramClient('search_session', API_ID, API_HASH)
    await client.start(PHONE)
    
    channel = await client.get_entity(MY_CHANNEL_ID)
    print(f'🔍 Ищем "{app_name}" в канале: {channel.title}')
    print('='*50)
    
    found_messages = []
    
    async for message in client.iter_messages(channel):
        if message.text and app_name in message.text:
            found_messages.append(message)
    
    if found_messages:
        print(f'📱 Найдено {len(found_messages)} сообщений с "{app_name}":')
        print()
        
        for i, msg in enumerate(found_messages, 1):
            print(f'--- Сообщение {i} ---')
            print(f'📅 Дата: {msg.date}')
            print(f'📝 Текст:')
            print(msg.text[:500])
            print()
            
            # Определяем тип сообщения
            if 'Тип: new_app' in msg.text:
                print('✅ ТИП: Новое приложение')
            elif 'Тип: ban' in msg.text:
                print('❌ ТИП: Бан приложения')
            elif 'Тип: redirect' in msg.text:
                print('🔄 ТИП: Редирект')
            print('='*50)
    else:
        print(f'❌ Сообщения с "{app_name}" не найдены')
    
    await client.disconnect()

if __name__ == "__main__":
    app_name = sys.argv[1] if len(sys.argv) > 1 else "Plinko Tap"
    asyncio.run(search_app(app_name)) 