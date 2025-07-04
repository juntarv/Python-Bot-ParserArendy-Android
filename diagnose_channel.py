from telethon import TelegramClient
import asyncio
from config import API_ID, API_HASH, PHONE, MY_CHANNEL_ID

client = TelegramClient('diagnose_session', API_ID, API_HASH)

async def diagnose_channel():
    await client.start(PHONE)
    print("✅ Подключено к Telegram\n")
    
    # Получаем канал
    channel = await client.get_entity(MY_CHANNEL_ID)
    print(f"📨 Канал: {channel.title}")
    print("=" * 50)
    
    # Читаем последние 10 сообщений для анализа
    print("\n📋 Последние 10 сообщений для анализа:\n")
    
    message_count = 0
    message_types = {'new_app': 0, 'ban': 0, 'bundle': 0, 'other': 0}
    bots_found = set()
    
    async for message in client.iter_messages(channel, limit=10):
        message_count += 1
        print(f"\n--- Сообщение #{message_count} (ID: {message.id}) ---")
        print(f"Дата: {message.date.strftime('%d.%m.%Y %H:%M')}")
        
        if message.text:
            # Показываем первые 200 символов
            preview = message.text[:200] + "..." if len(message.text) > 200 else message.text
            print(f"Текст: {preview}")
            
            # Анализируем структуру
            text = message.text
            
            # Ищем упоминания ботов
            import re
            bot_match = re.search(r'@(\w+)', text)
            if bot_match:
                bot_username = bot_match.group(1)
                bots_found.add(bot_username)
                print(f"✓ Найден бот: @{bot_username}")
            
            # Определяем тип
            if '🚀' in text or 'new_app' in text.lower():
                message_types['new_app'] += 1
                print("✓ Тип: Новое приложение")
            elif '❌' in text or 'ban' in text.lower():
                message_types['ban'] += 1
                print("✓ Тип: Бан")
            elif '📦' in text or 'bundle' in text.lower():
                message_types['bundle'] += 1
                print("✓ Тип: Bundle")
            else:
                message_types['other'] += 1
                print("✓ Тип: Другое")
            
            # Ищем название приложения
            app_patterns = [
                r'📱 \*\*Приложение:\*\* (.+)',
                r'Название:\s*(.+)',
                r'Приложение:\s*(.+)',
                r'Application\s+(.+?)\s+BANNED',
            ]
            
            for pattern in app_patterns:
                app_match = re.search(pattern, text)
                if app_match:
                    print(f"✓ Приложение: {app_match.group(1)}")
                    break
            
            # Ищем Bundle ID
            bundle_patterns = [
                r'📦 \*\*Bundle ID:\*\* (.+)',
                r'Bundle:\s*([^\s\n]+)',
                r'Имя пакета:\s*([^\s\n]+)',
                r'id=([^\s&]+)',
            ]
            
            for pattern in bundle_patterns:
                bundle_match = re.search(pattern, text)
                if bundle_match:
                    print(f"✓ Bundle: {bundle_match.group(1)}")
                    break
        else:
            print("Текст: [Пустое сообщение или медиа]")
    
    # Итоговая статистика
    print("\n" + "=" * 50)
    print("📊 СТАТИСТИКА КАНАЛА:")
    print(f"Проанализировано сообщений: {message_count}")
    print(f"\nТипы сообщений:")
    for msg_type, count in message_types.items():
        print(f"  {msg_type}: {count}")
    print(f"\nНайденные боты: {', '.join('@' + bot for bot in bots_found) if bots_found else 'Не найдено'}")
    
    # Полный анализ канала
    print("\n📊 ПОЛНЫЙ АНАЛИЗ КАНАЛА:")
    total_messages = 0
    apps_data = []
    
    async for message in client.iter_messages(channel, limit=None):
        total_messages += 1
        
        if message.text and '@' in message.text:
            # Простая проверка на наличие данных о приложении
            if any(word in message.text.lower() for word in ['приложение', 'app', 'bundle', 'название']):
                apps_data.append(message.id)
    
    print(f"Всего сообщений в канале: {total_messages}")
    print(f"Сообщений с данными о приложениях: {len(apps_data)}")
    
    if len(apps_data) == 0:
        print("\n⚠️ ПРОБЛЕМА: Не найдено сообщений с данными о приложениях!")
        print("Возможные причины:")
        print("1. Сообщения имеют другой формат")
        print("2. Скрипт load_history.py еще не запускался")
        print("3. Сообщения были удалены")
        
        print("\n💡 РЕКОМЕНДАЦИЯ:")
        print("Запустите сначала: python load_history.py")
        print("Это заполнит канал правильно отформатированными сообщениями")

async def main():
    try:
        await diagnose_channel()
    finally:
        await client.disconnect()

if __name__ == '__main__':
    print("🔍 Диагностика канала")
    print("=" * 50)
    asyncio.run(main())