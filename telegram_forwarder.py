from telethon import TelegramClient, events
import asyncio
import re
from datetime import datetime

# Настройки Telegram API
api_id = '21300389'  # Получить на https://my.telegram.org
api_hash = 'acf2f54b7dd38ae4ca633427f7d7f32c'
phone = '+380962820343'

# ID вашего канала для пересылки (начинается с -100)
MY_CHANNEL_ID =  -1002568412343  # Замените на ID вашего канала

# Список ботов конкурентов (username без @)
COMPETITOR_BOTS = [
    'wwapps_bot',
    #'competitor2_bot', 
    #'competitor3_bot',
    # Добавьте всех нужных ботов
]

# Создаем клиент
client = TelegramClient('session_name', api_id, api_hash)

# Паттерны для определения важных сообщений
PATTERNS = {
    'new_app': [
        r'(?:вышло|Доступно|новое приложение|released|launched|new app)',
        r'(?:теперь доступно|now available|появилось)'
    ],
    'ban': [
        r'(?:BAN|удалили|banned|removed|заблокировали)',
        r'(?:приложение удалено|app removed)'
    ]
}

def identify_message_type(text):
    """Определяет тип сообщения"""
    text_lower = text.lower()
    
    for msg_type, patterns in PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                return msg_type
    return 'other'

async def main():
    await client.start(phone)
    print("Бот запущен и готов к работе!")
    
    # Получаем entity вашего канала
    my_channel = await client.get_entity(MY_CHANNEL_ID)
    
    # Обработчик новых сообщений
    @client.on(events.NewMessage(from_users=COMPETITOR_BOTS))
    async def handler(event):
        try:
            # Получаем информацию об отправителе
            sender = await event.get_sender()
            bot_username = sender.username
            
            # Определяем тип сообщения
            message_type = identify_message_type(event.text)
            
            # Формируем сообщение для пересылки
            forward_text = f"""📨 **Новое от @{bot_username}**
🤖 **Бот:** {sender.first_name}
📅 **Время:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
🏷️ **Тип:** {message_type}

**Сообщение:**
{event.text}

{'🔗 ' + event.message.entities[0].url if event.message.entities else ''}
{'---' * 10}"""
            
            # Отправляем в ваш канал
            await client.send_message(my_channel, forward_text)
            
            print(f"✅ Переслано сообщение от @{bot_username}")
            
            # Если есть фото или документы, пересылаем и их
            if event.message.media:
                await client.send_file(my_channel, event.message.media)
                
        except Exception as e:
            print(f"❌ Ошибка: {e}")
    
    # Команда для проверки работы
    @client.on(events.NewMessage(pattern='/status'))
    async def status_handler(event):
        if event.sender_id == (await client.get_me()).id:
            await event.reply(f"✅ Бот работает\n📊 Отслеживаю {len(COMPETITOR_BOTS)} ботов")
    
    print("Отслеживаю сообщения от ботов:")
    for bot in COMPETITOR_BOTS:
        print(f"  - @{bot}")
    
    # Держим скрипт запущенным
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())