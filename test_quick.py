#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from telethon import TelegramClient
from config import *
from channel_to_sheets import parse_message_data

async def test_plinko_tap():
    client = TelegramClient('test_session', API_ID, API_HASH)
    await client.start(PHONE)
    
    channel = await client.get_entity(MY_CHANNEL_ID)
    print('🔍 Ищем сообщения Plinko Tap и тестируем обработку...')
    
    new_app_msg = None
    ban_msg = None
    
    # Находим оба сообщения
    plinko_messages = []
    async for message in client.iter_messages(channel):
        if message.text and 'Plinko Tap' in message.text:
            plinko_messages.append(message)
            print(f'📝 Найдено сообщение с Plinko Tap:')
            print(f'   Дата: {message.date}')
            print(f'   Содержит "Тип: new_app": {"Тип: new_app" in message.text}')
            print(f'   Содержит "Тип: ban": {"Тип: ban" in message.text}')
            print(f'   Первые 200 символов: {message.text[:200]}...')
            print()
    
    print(f'Всего найдено сообщений с Plinko Tap: {len(plinko_messages)}')
    
    for msg in plinko_messages:
        if 'Тип:** new_app' in msg.text:
            new_app_msg = msg
        elif 'Тип:** ban' in msg.text:
            ban_msg = msg
    
    if new_app_msg and ban_msg:
        print('✅ Найдены оба сообщения!')
        
        # Парсим новое приложение
        new_data = parse_message_data(new_app_msg.text)
        print(f'\n📱 Данные нового приложения:')
        print(f'   Название: "{new_data["app_name"]}"')
        print(f'   Тип: {new_data["type"]}')
        
        # Парсим бан
        ban_data = parse_message_data(ban_msg.text)
        print(f'\n❌ Данные бана:')
        print(f'   Название: "{ban_data["app_name"]}"')
        print(f'   Тип: {ban_data["type"]}')
        
        # Проверяем совпадение
        print(f'\n🔍 Сравнение:')
        print(f'   new_app название: "{new_data["app_name"]}" (длина: {len(new_data["app_name"])})')
        print(f'   ban название: "{ban_data["app_name"]}" (длина: {len(ban_data["app_name"])})')
        print(f'   Равны ли? {new_data["app_name"] == ban_data["app_name"]}')
        
        if new_data["app_name"] != ban_data["app_name"]:
            print(f'   Байты new_app: {new_data["app_name"].encode("utf-8")}')
            print(f'   Байты ban: {ban_data["app_name"].encode("utf-8")}')
    else:
        print('❌ Не найдены оба сообщения')
        
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(test_plinko_tap()) 