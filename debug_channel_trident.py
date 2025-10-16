from telethon import TelegramClient
import asyncio
from config import API_ID, API_HASH, MY_CHANNEL_ID

# Создаем клиент Telegram
client = TelegramClient('sessions/history_session', API_ID, API_HASH)

async def debug_channel_trident():
    """Показывает сообщения от Trident в канале для отладки"""
    await client.start()
    
    try:
        channel = await client.get_entity(MY_CHANNEL_ID)
        print(f"📨 Отладка канала: {channel.title}")
        
        print("\n🔍 Ищу сообщения от Trident в канале:")
        count = 0
        trident_count = 0
        
        async for message in client.iter_messages(channel, limit=50):
            if message.text:
                count += 1
                
                # Проверяем есть ли упоминания Trident
                if 'trident' in message.text.lower() or 'Trident' in message.text:
                    trident_count += 1
                    print(f"\n--- Сообщение Trident #{trident_count} ---")
                    
                    # Показываем начало сообщения
                    text_preview = message.text[:300] + "..." if len(message.text) > 300 else message.text
                    print(f"Текст: {text_preview}")
                    
                    # Проверяем критерии фильтра
                    has_bot_marker = '🤖 Бот:' in message.text
                    has_trident = 'Trident' in message.text or 'trident_appbot' in message.text
                    
                    print(f"Содержит '🤖 Бот:': {has_bot_marker}")
                    print(f"Содержит Trident: {has_trident}")
                    print(f"Подходит для обработки: {has_bot_marker and has_trident}")
        
        print(f"\n✅ Проверено сообщений: {count}")
        print(f"🔱 Найдено сообщений Trident: {trident_count}")
        
    finally:
        await client.disconnect()

if __name__ == "__main__":
    print("🔱 Отладка сообщений Trident в канале")
    print("=" * 40)
    asyncio.run(debug_channel_trident()) 