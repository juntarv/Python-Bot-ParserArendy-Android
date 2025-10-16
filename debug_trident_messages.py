#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from telethon import TelegramClient
from datetime import datetime, timedelta
import asyncio
import re
from config import *

# Создаем клиент Telegram
client = TelegramClient('sessions/history_session', API_ID, API_HASH)

async def debug_trident_messages():
    """Отладка сообщений от Trident App Bot"""
    await client.start()
    
    try:
        # Получаем бота
        trident_bot = await client.get_entity('trident_appbot')
        
        print(f"📨 Анализирую сообщения от @trident_appbot")
        
        # Дата начала (7 дней назад для отладки)
        start_date = datetime.now() - timedelta(days=7)
        print(f"📅 Начиная с: {start_date.strftime('%d.%m.%Y')}")
        
        checked_count = 0
        
        # Получаем последние 10 сообщений для анализа
        async for message in client.iter_messages(trident_bot, offset_date=start_date, limit=10):
            if message.text:
                checked_count += 1
                
                print(f"\n{'='*60}")
                print(f"СООБЩЕНИЕ #{checked_count}")
                print(f"Дата: {message.date}")
                print(f"ID: {message.id}")
                print(f"{'='*60}")
                print(f"ПОЛНЫЙ ТЕКСТ:")
                print(message.text)
                print(f"{'='*60}")
                
                # Анализируем ключевые слова
                text_lower = message.text.lower()
                
                # Проверяем на новые приложения
                new_app_keywords = ['добавлено', 'новое приложение', '🔥', 'добавили']
                found_new_keywords = [kw for kw in new_app_keywords if kw in text_lower]
                
                # Проверяем на баны
                ban_keywords = ['бан', 'в бане', '⛔', '🛑', 'забанено']
                found_ban_keywords = [kw for kw in ban_keywords if kw in text_lower]
                
                # Проверяем на пропуск
                skip_keywords = ['доступно к заливу', 'facebook', 'фб трафик', '🟢']
                found_skip_keywords = [kw for kw in skip_keywords if kw in text_lower]
                
                print(f"🔍 АНАЛИЗ КЛЮЧЕВЫХ СЛОВ:")
                print(f"  🆕 Новое приложение: {found_new_keywords}")
                print(f"  ❌ Бан: {found_ban_keywords}")
                print(f"  ⚠️ Пропуск: {found_skip_keywords}")
                
                # Ищем URL
                url_match = re.search(r'https://play\.google\.com/store/apps/details\?id=([^\s&)]+)', message.text)
                if url_match:
                    print(f"  🔗 Bundle ID: {url_match.group(1)}")
                else:
                    print(f"  🔗 Bundle ID: НЕ НАЙДЕН")
                
                # Попробуем найти название приложения разными способами
                print(f"\n🔍 ПОИСК НАЗВАНИЯ ПРИЛОЖЕНИЯ:")
                
                # Паттерн 1: После "🔥Добавлено новое приложение"
                name_pattern1 = r'🔥\s*Добавлено новое приложение\s+(.+?)\s+\(https'
                match1 = re.search(name_pattern1, message.text)
                if match1:
                    print(f"  📱 Паттерн 1 (новое): '{match1.group(1)}'")
                
                # Паттерн 2: После "⛔️ Приложение:"
                name_pattern2 = r'⛔️\s*Приложение:\s*(.+?)\s+\(https'
                match2 = re.search(name_pattern2, message.text)
                if match2:
                    print(f"  📱 Паттерн 2 (бан ⛔): '{match2.group(1)}'")
                
                # Паттерн 3: После "🛑 Приложение:"
                name_pattern3 = r'🛑\s*Приложение:\s*(.+?)\s+в\s+бане'
                match3 = re.search(name_pattern3, message.text)
                if match3:
                    print(f"  📱 Паттерн 3 (бан 🛑): '{match3.group(1)}'")
                
                # Паттерн 4: Общий поиск названий
                general_patterns = [
                    r'Приложение:\s*(.+?)(?:\s+\(|$)',
                    r'приложение\s+(.+?)(?:\s+\(|$)',
                    r'App:\s*(.+?)(?:\s+\(|$)'
                ]
                
                for i, pattern in enumerate(general_patterns, 4):
                    match = re.search(pattern, message.text, re.IGNORECASE)
                    if match:
                        print(f"  📱 Паттерн {i} (общий): '{match.group(1)}'")
                
                if not any([match1, match2, match3]):
                    print(f"  ❌ Название НЕ НАЙДЕНО стандартными паттернами")
        
        print(f"\n✅ Проанализировано сообщений: {checked_count}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    print("🔱 Отладка сообщений от Trident App Bot")
    print("=" * 50)
    asyncio.run(debug_trident_messages()) 