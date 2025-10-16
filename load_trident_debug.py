#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telethon import TelegramClient
from datetime import datetime, timedelta
import asyncio
import re
from config import *

# Создаем клиент Telegram
client = TelegramClient('sessions/trident_debug_session', API_ID, API_HASH)

def clean_app_name(name):
    """Очищает название приложения от лишних символов"""
    if not name:
        return name
    
    # Убираем эмодзи в начале
    name = re.sub(r'^[^\w\s]+\s*', '', name)
    
    # Убираем звездочки (markdown)
    name = re.sub(r'\*+', '', name)
    
    # Убираем квадратные скобки и их содержимое
    name = re.sub(r'\[.*?\]', '', name)
    
    # Убираем круглые скобки и их содержимое (может содержать URL)
    name = re.sub(r'\([^)]*\)', '', name)
    
    # Убираем лишние символы в конце типа ], }, ), >
    name = re.sub(r'[\]\}>)]+\s*$', '', name)
    
    # Убираем лишние пробелы
    name = re.sub(r'\s+', ' ', name).strip()
    
    return name

def parse_trident_message(text, message_id):
    """Парсит сообщение от Trident App Bot с отладкой"""
    print(f"\n--- ОТЛАДКА СООБЩЕНИЯ {message_id} ---")
    print(f"Исходный текст: {text[:200]}...")
    
    result = {
        'type': None,
        'name': '',
        'bundle': '',
        'url': ''
    }
    
    if not text:
        print("❌ Пустой текст")
        return result
    
    parser = BOT_PARSERS.get('trident_appbot', {})
    print(f"📋 Загружены паттерны: {list(parser.keys())}")
    
    # Проверяем паттерны пропуска
    skip_patterns = parser.get('skip_patterns', [])
    print(f"🔍 Проверяю паттерны пропуска: {skip_patterns}")
    for skip_pattern in skip_patterns:
        if re.search(skip_pattern, text, re.IGNORECASE):
            print(f"⚠️ ПРОПУСКАЮ - найден паттерн пропуска: {skip_pattern}")
            return result
    
    # Определяем тип сообщения
    new_app_patterns = parser.get('new_app_patterns', [])
    ban_patterns = parser.get('ban_patterns', [])
    
    print(f"🆕 Проверяю паттерны новых приложений: {new_app_patterns}")
    for pattern in new_app_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            result['type'] = 'new_app'
            print(f"✅ НАЙДЕН паттерн нового приложения: {pattern}")
            break
    
    if not result['type']:
        print(f"🚫 Проверяю паттерны банов: {ban_patterns}")
        for pattern in ban_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                result['type'] = 'ban'
                print(f"✅ НАЙДЕН паттерн бана: {pattern}")
                break
    
    if not result['type']:
        print("❌ Тип сообщения не определен")
        return result
    
    print(f"📋 Определен тип: {result['type']}")
    
    # Извлекаем название приложения
    if result['type'] == 'new_app':
        name_pattern = parser.get('name_pattern')
        print(f"🔍 Паттерн имени для new_app: {name_pattern}")
        if name_pattern:
            name_match = re.search(name_pattern, text)
            if name_match:
                result['name'] = clean_app_name(name_match.group(1).strip())
                print(f"✅ Найдено имя: '{result['name']}'")
            else:
                print("❌ Имя не найдено по паттерну")
    
    elif result['type'] == 'ban':
        ban_name_pattern = parser.get('ban_name_pattern')
        print(f"🔍 Паттерн имени для ban: {ban_name_pattern}")
        if ban_name_pattern:
            name_match = re.search(ban_name_pattern, text)
            if name_match:
                result['name'] = clean_app_name(name_match.group(1).strip())
                print(f"✅ Найдено имя забаненного: '{result['name']}'")
            else:
                print("❌ Имя забаненного не найдено по паттерну")
    
    # Извлекаем URL и Bundle ID
    url_pattern = parser.get('url_pattern')
    print(f"🔍 Паттерн URL: {url_pattern}")
    if url_pattern:
        url_match = re.search(url_pattern, text)
        if url_match:
            result['bundle'] = url_match.group(1)
            result['url'] = f"https://play.google.com/store/apps/details?id={result['bundle']}"
            print(f"✅ Найден Bundle ID: '{result['bundle']}'")
        else:
            print("❌ URL не найден")
    
    print(f"📋 Финальный результат: {result}")
    return result

def format_trident_message(data, bot_name, original_text):
    """Форматирует сообщение в единый стиль"""
    
    # Определяем эмодзи и тип
    if data['type'] == 'new_app':
        emoji = '🚀'
        msg_type_display = 'new_app'
    elif data['type'] == 'ban':
        emoji = '❌'
        msg_type_display = 'ban'
    else:
        emoji = '📝'
        msg_type_display = data['type']
    
    # Получаем текущее время
    current_time = datetime.now().strftime('%d.%m.%Y %H:%M')
    
    # Формируем сообщение
    message_parts = [
        f"{emoji} **История от @trident_appbot**",
        f"🤖 **Бот:** {bot_name}",
        f"📅 **Время:** {current_time}",
        f"🏷️ **Тип:** {msg_type_display}"
    ]
    
    # Добавляем информацию о приложении
    if data['type'] == 'new_app':
        message_parts.append(f"📱 **Приложение:** {data['name']}")
    elif data['type'] == 'ban':
        message_parts.append(f"📱 **Забанено:** {data['name']}")
    
    # Добавляем Bundle ID
    if data['bundle']:
        message_parts.append(f"📦 **Bundle ID:** {data['bundle']}")
    
    # Добавляем оригинальное сообщение
    message_parts.append(f"\n**Оригинальное сообщение:**")
    message_parts.append(original_text)
    
    # Добавляем ссылку
    if data['url']:
        message_parts.append(f"🔗 **Ссылка:** {data['url']}")
    
    return '\n'.join(message_parts)

async def collect_trident_messages():
    """Собирает сообщения от Trident App Bot с отладкой"""
    await client.start()
    
    try:
        # Получаем сущности
        my_channel = await client.get_entity(MY_CHANNEL_ID)
        trident_bot = await client.get_entity('trident_appbot')
        
        print(f"📨 Собираю сообщения от @trident_appbot")
        print(f"📤 Буду пересылать в: {my_channel.title}")
        
        # Дата начала (60 дней назад)
        start_date = datetime.now() - timedelta(days=DAYS_TO_LOAD)
        print(f"📅 Начиная с: {start_date.strftime('%d.%m.%Y')}")
        
        messages_collected = []
        checked_count = 0
        forwarded_count = 0
        
        # Собираем все сообщения от бота (ограничим первые 20 для отладки)
        async for message in client.iter_messages(trident_bot, offset_date=start_date, limit=20):
            if message.text:
                checked_count += 1
                
                print(f"\n{'='*50}")
                print(f"СООБЩЕНИЕ #{checked_count}")
                print(f"Дата: {message.date}")
                print(f"Полный текст:")
                print(message.text)
                print(f"{'='*50}")
                
                # Парсим сообщение
                parsed_data = parse_trident_message(message.text, checked_count)
                
                if parsed_data['type']:  # Если сообщение распарсилось
                    messages_collected.append((message, parsed_data))
                    print(f"✅ Сообщение добавлено в коллекцию")
                else:
                    print(f"❌ Сообщение не прошло парсинг")
        
        print(f"\n✅ Проверено сообщений: {checked_count}")
        print(f"📋 Найдено подходящих: {len(messages_collected)}")
        
        # Переворачиваем, чтобы пересылать от старых к новым
        messages_collected.reverse()
        
        # Пересылаем сообщения
        for message, parsed_data in messages_collected:
            formatted_message = format_trident_message(parsed_data, 'Trident Apps', message.text)
            
            await client.send_message(my_channel, formatted_message)
            forwarded_count += 1
            
            print(f"📤 Переслано: {forwarded_count}/{len(messages_collected)}")
            
            # Небольшая задержка для избежания флуда
            await asyncio.sleep(1.0)
        
        print(f"\n✅ Переслано сообщений: {forwarded_count}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    print("🔱 Сбор сообщений от Trident App Bot (DEBUG)")
    print("=" * 50)
    asyncio.run(collect_trident_messages()) 