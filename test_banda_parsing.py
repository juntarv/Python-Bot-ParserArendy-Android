from telethon import TelegramClient
import asyncio
from datetime import datetime, timedelta
from config import API_ID, API_HASH, PHONE, MY_CHANNEL_ID, BOT_PARSERS, DELAY_BETWEEN_MESSAGES
from load_history import parse_message_by_bot, extract_urls_from_message, extract_bundle_from_url

client = TelegramClient('debug_banda_session', API_ID, API_HASH)

async def debug_banda():
    await client.start(PHONE)
    print("✅ Подключено к Telegram\n")
    
    # Получаем бота и канал
    bot = await client.get_entity('banda_rent_apps_bot')
    my_channel = await client.get_entity(MY_CHANNEL_ID)
    
    print(f"📨 Анализирую сообщения от @banda_rent_apps_bot")
    print(f"📤 Буду пересылать в канал: {my_channel.title}")
    print("=" * 50)
    
    # Статистика
    stats = {
        'total': 0,
        'new_android': 0,
        'new_ios': 0,
        'bans': 0,
        'fb_blocks': 0,
        'fb_restored': 0,
        'other': 0,
        'forwarded': 0,
        'failed': 0
    }
    
    # Дата начала (30 дней назад)
    date_from = datetime.now() - timedelta(days=30)
    
    print(f"📅 Загружаю сообщения за последние 30 дней (с {date_from.strftime('%d.%m.%Y')})\n")
    
    # Обрабатываем сообщения
    async for message in client.iter_messages(bot, offset_date=date_from, reverse=True):
        if not message.text:
            continue
            
        stats['total'] += 1
        
        # Определяем тип сообщения и пересылаем нужные
        should_forward = False
        msg_type = None
        
        if '🎉 New Android App 🎉' in message.text:
            stats['new_android'] += 1
            should_forward = True
            msg_type = 'new_app'
            
        elif '🎉 New iOS App 🎉' in message.text:
            stats['new_ios'] += 1
            # iOS пропускаем
            
        elif 'BANNED' in message.text and '‼️' in message.text:
            stats['bans'] += 1
            should_forward = True
            msg_type = 'ban'
            
        elif 'Facebook has blocked' in message.text:
            stats['fb_blocks'] += 1
            
        elif 'Facebook ID has been changed' in message.text:
            stats['fb_restored'] += 1
            
        else:
            stats['other'] += 1
        
        # Пересылаем если нужно
        if should_forward:
            try:
                # Парсим сообщение
                parsed_data = parse_message_by_bot(message, 'banda_rent_apps_bot')
                
                if parsed_data:
                    print(f"\n📨 Обрабатываю {msg_type} сообщение ID: {message.id}")
                    print(f"   Распарсено: название='{parsed_data.get('name')}', bundle='{parsed_data.get('bundle')}'")
                    
                    # Формируем текст для пересылки
                    emoji = '🚀' if msg_type == 'new_app' else '❌'
                    
                    forward_text = f"""{emoji} **История от @banda_rent_apps_bot**
🤖 **Бот:** Banda Apps
📅 **Время:** {message.date.strftime('%d.%m.%Y %H:%M')}
🏷️ **Тип:** {msg_type}
{f'📱 **Приложение:** {parsed_data["name"]}' if parsed_data.get('name') else '📱 **Приложение:** [Не распознано]'}
{f'📦 **Bundle ID:** {parsed_data["bundle"]}' if parsed_data.get('bundle') else ''}

**Сообщение:**
{message.text}"""

                    # Добавляем ссылку
                    if parsed_data.get('url'):
                        forward_text += f"\n\n🔗 **Ссылка:** {parsed_data['url']}"
                    
                    forward_text += f"\n\n{'---' * 10}"
                    
                    # Отправляем в канал
                    await client.send_message(my_channel, forward_text)
                    stats['forwarded'] += 1
                    print(f"   ✅ Переслано в канал")
                    
                    # Задержка
                    await asyncio.sleep(DELAY_BETWEEN_MESSAGES)
                else:
                    print(f"\n⚠️ Не удалось распарсить {msg_type} сообщение ID: {message.id}")
                    print(f"   Текст: {message.text[:100]}...")
                    stats['failed'] += 1
                    
            except Exception as e:
                print(f"\n❌ Ошибка при обработке сообщения ID {message.id}: {e}")
                stats['failed'] += 1
                
                # Если flood wait
                if "wait of" in str(e):
                    wait_seconds = int(str(e).split("wait of ")[1].split(" seconds")[0])
                    print(f"   ⏰ Жду {wait_seconds} секунд...")
                    await asyncio.sleep(wait_seconds + 5)
        
        # Прогресс
        if stats['total'] % 10 == 0:
            print(f"Обработано: {stats['total']} сообщений...", end='\r')
    
    # Выводим итоговую статистику
    print("\n\n" + "=" * 50)
    print("📊 ИТОГОВАЯ СТАТИСТИКА:")
    print(f"Всего сообщений: {stats['total']}")
    print(f"├─ 🎉 Новые Android приложения: {stats['new_android']}")
    print(f"├─ 🎉 Новые iOS приложения: {stats['new_ios']} (пропущено)")
    print(f"├─ ❌ Баны приложений: {stats['bans']}")
    print(f"├─ 🚫 FB заблокировал: {stats['fb_blocks']} (пропущено)")
    print(f"├─ ✅ FB восстановлен: {stats['fb_restored']} (пропущено)")
    print(f"└─ ❓ Другие: {stats['other']} (пропущено)")
    print(f"\n✅ Успешно переслано: {stats['forwarded']}")
    print(f"❌ Не удалось обработать: {stats['failed']}")

async def main():
    try:
        await debug_banda()
    finally:
        await client.disconnect()

if __name__ == '__main__':
    print("🔍 Отладка и пересылка сообщений от banda_rent_apps_bot")
    print("=" * 50)
    asyncio.run(main())