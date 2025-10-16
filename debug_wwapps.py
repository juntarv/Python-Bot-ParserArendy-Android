from telethon import TelegramClient
import asyncio
from config import API_ID, API_HASH, MY_CHANNEL_ID

# Создаем клиент Telegram
client = TelegramClient('sessions/history_session', API_ID, API_HASH)

async def debug_channel_messages():
    """Показывает последние сообщения в канале для отладки"""
    await client.start()
    
    try:
        channel = await client.get_entity(MY_CHANNEL_ID)
        print(f"📨 Отладка канала: {channel.title}")
        
        print("\n🔍 Последние 10 сообщений в канале:")
        count = 0
        
        async for message in client.iter_messages(channel, limit=10):
            if message.text:
                count += 1
                print(f"\n--- Сообщение {count} ---")
                
                # Показываем начало сообщения
                text_preview = message.text[:200] + "..." if len(message.text) > 200 else message.text
                print(f"Текст: {text_preview}")
                
                # Проверяем критерии фильтра
                has_bot_marker = '🤖 Бот:' in message.text
                has_wwapps = 'WildWildApps' in message.text or 'wwapps_bot' in message.text
                
                print(f"Содержит '🤖 Бот:': {has_bot_marker}")
                print(f"Содержит WWApps: {has_wwapps}")
                print(f"Подходит для обработки: {has_bot_marker and has_wwapps}")
        
        print(f"\n✅ Проверено {count} сообщений")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    print("🔍 Отладка сообщений WWApps")
    print("=" * 40)
    asyncio.run(debug_channel_messages()) 