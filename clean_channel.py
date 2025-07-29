from telethon import TelegramClient
import asyncio
from config import API_ID, API_HASH, PHONE, MY_CHANNEL_ID

# Создаем клиент
client = TelegramClient('clear_channel_session', API_ID, API_HASH)

async def clear_channel():
    """Удаляет все сообщения из канала"""
    await client.start(PHONE)
    print("✅ Подключено к Telegram")
    
    try:
        # Получаем канал
        channel = await client.get_entity(MY_CHANNEL_ID)
        print(f"📨 Канал: {channel.title}")
        
        # Подтверждение
        print(f"\n⚠️  ВНИМАНИЕ! Это действие удалит ВСЕ сообщения из канала!")
        print(f"📍 Канал: {channel.title}")
        confirm = input("\nВы уверены? Введите 'ДА' для подтверждения: ")
        
        if confirm != 'ДА':
            print("❌ Операция отменена")
            return
        
        print("\n🗑️ Начинаю удаление сообщений...")
        
        # Счетчик удаленных сообщений
        deleted_count = 0
        batch_size = 100  # Удаляем по 100 сообщений за раз
        
        while True:
            # Получаем сообщения
            messages = []
            async for message in client.iter_messages(channel, limit=batch_size):
                messages.append(message.id)
            
            if not messages:
                break
            
            # Удаляем пачкой
            await client.delete_messages(channel, messages)
            deleted_count += len(messages)
            
            print(f"  ✅ Удалено: {deleted_count} сообщений", end='\r')
            
            # Небольшая задержка чтобы не получить флуд
            await asyncio.sleep(1)
        
        print(f"\n\n✅ Готово! Удалено {deleted_count} сообщений")
        print(f"🧹 Канал '{channel.title}' полностью очищен")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
    finally:
        await client.disconnect()
        print("\n👋 Отключено от Telegram")

async def clear_channel_no_confirm():
    """Удаляет все сообщения без подтверждения (для автоматизации)"""
    await client.start(PHONE)
    
    try:
        channel = await client.get_entity(MY_CHANNEL_ID)
        deleted_count = 0
        
        while True:
            messages = []
            async for message in client.iter_messages(channel, limit=100):
                messages.append(message.id)
            
            if not messages:
                break
            
            await client.delete_messages(channel, messages)
            deleted_count += len(messages)
            await asyncio.sleep(1)
        
        return deleted_count
        
    finally:
        await client.disconnect()

async def quick_clear_channel():
    """Быстро очищает канал без подтверждения и с минимальным выводом"""
    await client.start(PHONE)
    
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
            
            await asyncio.sleep(0.5)  # Уменьшаем задержку
        
        print(f"✅ Канал очищен! Удалено {deleted_count} сообщений")
        return deleted_count
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return 0
    finally:
        await client.disconnect()

if __name__ == '__main__':
    print("🗑️ Очистка канала Telegram")
    print("=" * 50)
    asyncio.run(clear_channel())
    print("🗑️ Быстрая очистка канала...")
    asyncio.run(quick_clear_channel())