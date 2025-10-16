from telethon import TelegramClient
import asyncio
from config import API_ID, API_HASH, MY_CHANNEL_ID

# Используем существующую сессию
client = TelegramClient('sessions/history_session', API_ID, API_HASH)

async def quick_clear_channel():
    """Быстро очищает канал без подтверждения"""
    await client.start()
    
    try:
        channel = await client.get_entity(MY_CHANNEL_ID)
        print(f"🧹 Очищаю канал: {channel.title}")
        
        deleted_count = 0
        batch_size = 100
        
        while True:
            messages = []
            async for message in client.iter_messages(channel, limit=batch_size):
                messages.append(message.id)
            
            if not messages:
                break
            
            await client.delete_messages(channel, messages)
            deleted_count += len(messages)
            
            if deleted_count % 500 == 0:
                print(f"  🗑️ Удалено: {deleted_count} сообщений")
            
            await asyncio.sleep(0.5)
        
        print(f"✅ Канал очищен! Удалено {deleted_count} сообщений")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 0
    finally:
        await client.disconnect()

if __name__ == '__main__':
    print("🧹 Автоматическая очистка канала...")
    asyncio.run(quick_clear_channel()) 