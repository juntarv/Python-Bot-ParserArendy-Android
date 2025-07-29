from telethon import TelegramClient
from datetime import datetime, timedelta
import asyncio
import re
from config import *  # Импортируем все настройки

# Создаем клиент
client = TelegramClient('history_session', API_ID, API_HASH)

def extract_bundle_from_url(url):
    """Извлекает bundle ID из URL Google Play"""
    if not url:
        return None
    
    # Паттерн для Google Play URL
    match = re.search(r'id=([^\s&]+)', url)
    if match:
        return match.group(1)
    return None

def extract_urls_from_message(message):
    """Извлекает URL из сообщения, включая гиперссылки"""
    urls = []
    
    # Если есть entities (форматирование текста)
    if message.entities:
        for entity in message.entities:
            # MessageEntityTextUrl - это гиперссылка
            if hasattr(entity, 'url') and entity.url:
                urls.append(entity.url)
    
    # Также ищем обычные URL в тексте
    if message.text:
        url_pattern = r'https?://[^\s\)]+'
        found_urls = re.findall(url_pattern, message.text)
        urls.extend(found_urls)
    
    # Убираем дубликаты
    return list(set(urls))

def parse_message_by_bot(message, bot_username):
    """Парсит сообщение в зависимости от бота"""
    if bot_username not in BOT_PARSERS:
        return None
    
    parser = BOT_PARSERS[bot_username]
    text = message.text
    if not text:
        return None
    
    # Проверяем, нужно ли пропустить сообщение
    for skip_pattern in parser.get('skip_patterns', []):
        if re.search(skip_pattern, text, re.IGNORECASE):
            return None
    
    result = {
        'type': None,
        'name': None,
        'bundle': None,
        'url': None,
        'category': None,
        'is_bundle': False,
        'geo_restrictions': None,
        'sources': None,
        'has_onelink': False,
        'has_macro_system': False,
        'redirect_to': None,
        'original_app': None
    }
    
    # Извлекаем URL из сообщения
    urls = extract_urls_from_message(message)
    result['url'] = urls[0] if urls else None
    
    # Определяем тип сообщения
    for pattern in parser.get('new_app_patterns', []):
        if re.search(pattern, text, re.IGNORECASE):
            result['type'] = 'new_app'
            break
    
    if not result['type']:
        for pattern in parser.get('ban_patterns', []):
            if re.search(pattern, text, re.IGNORECASE):
                result['type'] = 'ban'
                break
    
    # Проверяем на redirect (перенаправление трафика)
    if not result['type'] and parser.get('redirect_patterns'):
        for pattern in parser.get('redirect_patterns', []):
            if re.search(pattern, text, re.IGNORECASE):
                result['type'] = 'redirect'
                break
    
    if not result['type']:
        return None
    
    # Специальная обработка для Banda Apps
    if bot_username == 'banda_rent_apps_bot':
        # Для новых приложений
        if result['type'] == 'new_app':
            # Извлекаем название (убираем эмодзи)
            name_match = re.search(parser['name_pattern'], text, re.IGNORECASE)
            if name_match:
                name_text = name_match.group(1).strip()
                # Убираем эмодзи из начала названия
                name_text = re.sub(r'^[^\w\s]+\s*', '', name_text)
                result['name'] = name_text.strip()
            
            # Извлекаем гео-ограничения
            if parser.get('geo_pattern'):
                geo_match = re.search(parser['geo_pattern'], text)
                if geo_match:
                    result['geo_restrictions'] = geo_match.group(1).strip()
            
            # Извлекаем источники трафика
            if parser.get('sources_pattern'):
                sources_match = re.search(parser['sources_pattern'], text)
                if sources_match:
                    result['sources'] = sources_match.group(1).strip()
            
            # Проверяем поддержку OneLink
            if parser.get('onelink_pattern'):
                result['has_onelink'] = bool(re.search(parser['onelink_pattern'], text, re.IGNORECASE))
            
            # Проверяем систему автосбора макросов
            if parser.get('macro_pattern'):
                result['has_macro_system'] = bool(re.search(parser['macro_pattern'], text, re.IGNORECASE))
        
        # Для банов
        elif result['type'] == 'ban':
            ban_name_match = re.search(parser['ban_name_pattern'], text)
            if ban_name_match:
                name_text = ban_name_match.group(1).strip()
                # Убираем эмодзи
                name_text = re.sub(r'^[^\w\s]+\s*', '', name_text)
                result['name'] = name_text.strip()
            
            # Ищем URL в скобках
            if not result['url']:
                url_match = re.search(r'\((https?://[^\)]+)\)', text)
                if url_match:
                    result['url'] = url_match.group(1)
        
        # Для редиректов (новый тип)
        elif result['type'] == 'redirect':
            # Извлекаем исходное приложение и новое
            redirect_match = re.search(parser.get('redirect_name_pattern', ''), text)
            if redirect_match:
                result['redirect_to'] = redirect_match.group(1).strip()
                result['bundle'] = redirect_match.group(2).strip()
            
            # Ищем оригинальное забаненное приложение
            original_match = re.search(r'Application\s+(.+?)\s+BANNED', text)
            if original_match:
                result['original_app'] = original_match.group(1).strip()
                result['original_app'] = re.sub(r'^[^\w\s]+\s*', '', result['original_app'])
        
        # Извлекаем bundle из URL для всех типов
        if not result['bundle'] and result['url']:
            result['bundle'] = extract_bundle_from_url(result['url'])
    
    # Обработка для других ботов (оставляем как было)
    else:
    # Извлекаем название приложения
    if result['type'] == 'ban' and 'ban_name_pattern' in parser:
        name_match = re.search(parser['ban_name_pattern'], text)
        if name_match:
            name_text = name_match.group(1).strip()
            name_text = re.sub(r'^[^\w\s]+\s*', '', name_text)
            result['name'] = name_text.strip()
    elif parser.get('name_pattern'):
        name_match = re.search(parser['name_pattern'], text)
        if name_match:
            name_text = name_match.group(1).strip()
            
            if parser.get('url_in_name'):
                url_in_name = re.search(r'\(?(https?://[^\s\)]+)\)?', name_text)
                if url_in_name:
                    if not result['url']:
                        result['url'] = url_in_name.group(1)
                    name_text = re.sub(r'\s*\(?(https?://[^\s\)]+)\)?', '', name_text).strip()
            
            result['name'] = name_text
    
    # Извлекаем bundle
    if parser.get('bundle_pattern'):
        bundle_match = re.search(parser['bundle_pattern'], text)
        if bundle_match:
            result['bundle'] = bundle_match.group(1).strip()
    
    # Если bundle не найден, но есть URL и нужно извлечь из него
    if not result['bundle'] and parser.get('extract_bundle_from_url') and result['url']:
            result['bundle'] = extract_bundle_from_url(result['url'])
    
    # Извлекаем категорию (если есть)
    if parser.get('category_pattern'):
        category_match = re.search(parser['category_pattern'], text)
        if category_match:
            result['category'] = category_match.group(1).strip()
    
    # Определяем, является ли это Bundle (по тексту)
    if 'bundle' in text.lower() and result['type'] == 'new_app':
        result['is_bundle'] = True
    
    return result

def is_bundle(text):
    """Проверяет, является ли приложение Bundle"""
    if not text:
        return False
    
    text_lower = text.lower()
    bundle_keywords = KEYWORDS.get('bundle', [])
    
    for keyword in bundle_keywords:
        if keyword.lower() in text_lower:
            return True
    return False

def detect_message_type(text):
    """Определяет тип сообщения по ключевым словам"""
    if not text:
        return None, 'other'
    
    text_lower = text.lower()
    
    # Проверяем каждую категорию
    for category, keywords in KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return keyword, category
    
    return None, 'other'

def should_forward_message(text):
    """Проверяет, нужно ли пересылать сообщение"""
    if not FILTER_BY_KEYWORDS:
        return True
    
    if not text or len(text) < MIN_MESSAGE_LENGTH:
        return False
    
    text_lower = text.lower()
    
    # Проверяем наличие любого ключевого слова
    for keyword in ALL_KEYWORDS:
        if keyword.lower() in text_lower:
            return True
    
    return False

def extract_app_name(text):
    """Пытается извлечь название приложения из текста"""
    # Паттерны для поиска названий в кавычках
    patterns = [
        r'"([^"]+)"',  # В двойных кавычках
        r'«([^»]+)»',  # В кавычках-елочках
        r'"([^"]+)"',  # В английских кавычках
        r'\'([^\']+)\'',  # В одинарных кавычках
        r'\[([^\]]+)\]',  # В квадратных скобках
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    
    # Если не нашли в кавычках, ищем после ключевых слов
    app_patterns = [
        r'(?:приложение|app|игра|game)\s+(\S+)',
        r'(?:вышло|запустили|launched)\s+(\S+)',
    ]
    
    for pattern in app_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return None

def format_unified_message(parsed_data, bot_username, bot_display_name, message_date, original_text):
    """Создает единообразно отформатированное сообщение для любого бота"""
    
    # Выбираем эмодзи в зависимости от типа
    emoji_map = {
        'new_app': '🚀',
        'ban': '❌', 
        'redirect': '🔄',
        'update': '🔄',
        'bundle': '📦'
    }
    
    msg_type = parsed_data.get('type', 'other')
    
    # Для bundle приложений используем специальный эмодзи
    if parsed_data.get('is_bundle') and msg_type == 'new_app':
        emoji = emoji_map.get('bundle', '📦')
        msg_type_display = f"{msg_type} (Bundle)"
    else:
        emoji = emoji_map.get(msg_type, '📨')
        msg_type_display = msg_type
    
    # Базовая информация (одинаковая для всех ботов)
    forward_text = f"""{emoji} **История от @{bot_username}**
🤖 **Бот:** {bot_display_name}
📅 **Время:** {message_date.strftime('%d.%m.%Y %H:%M')}
🏷️ **Тип:** {msg_type_display}"""
    
    # Добавляем информацию в зависимости от типа сообщения
    if msg_type == 'new_app':
        if parsed_data.get('name'):
            forward_text += f"\n📱 **Приложение:** {parsed_data['name']}"
        
        # Дополнительная информация для Banda Apps
        if bot_username == 'banda_rent_apps_bot':
            if parsed_data.get('geo_restrictions'):
                forward_text += f"\n🌍 **Гео-ограничения:** {parsed_data['geo_restrictions']}"
            if parsed_data.get('sources'):
                forward_text += f"\n📊 **Источники:** {parsed_data['sources']}"
            if parsed_data.get('has_onelink'):
                forward_text += f"\n🔗 **OneLink:** Поддерживается"
            if parsed_data.get('has_macro_system'):
                forward_text += f"\n🤖 **Автосбор макросов:** Есть"
        
        # Категория для других ботов
        if parsed_data.get('category'):
            forward_text += f"\n📂 **Категория:** {parsed_data['category']}"
    
    elif msg_type == 'ban':
        if parsed_data.get('name'):
            forward_text += f"\n📱 **Забанено:** {parsed_data['name']}"
    
    elif msg_type == 'redirect':
        if parsed_data.get('original_app'):
            forward_text += f"\n❌ **Забанено:** {parsed_data['original_app']}"
        if parsed_data.get('redirect_to'):
            forward_text += f"\n🔄 **Перенаправлено на:** {parsed_data['redirect_to']}"
    
    # Bundle ID (для всех типов если есть)
    if parsed_data.get('bundle'):
        forward_text += f"\n📦 **Bundle ID:** {parsed_data['bundle']}"
    
    # Оригинальное сообщение
    forward_text += f"\n\n**Оригинальное сообщение:**\n{original_text}"
    
    # Ссылка (если есть)
    if parsed_data.get('url'):
        forward_text += f"\n\n🔗 **Ссылка:** {parsed_data['url']}"
    
    forward_text += f"\n\n{'---' * 10}"
    
    return forward_text

async def load_history():
    await client.start(PHONE)
    print("✅ Подключено к Telegram")
    
    # Получаем entity канала
    my_channel = await client.get_entity(MY_CHANNEL_ID)
    
    # Дата, с которой загружаем
    date_from = datetime.now() - timedelta(days=DAYS_TO_LOAD)
    
    print(f"\n📅 Загружаю сообщения за последние {DAYS_TO_LOAD} дней")
    print(f"📅 Начиная с: {date_from.strftime('%d.%m.%Y')}")
    print(f"🔍 Фильтрация: {'Включена' if FILTER_BY_KEYWORDS else 'Выключена'}")
    print(f"🖼️ Пересылка медиа: {'Включена' if FORWARD_MEDIA else 'Выключена'}")
    if FILTER_BY_KEYWORDS:
        print(f"📝 Ключевых слов для поиска: {len(ALL_KEYWORDS)}")
    print("-" * 50)
    
    # Статистика
    stats = {
        'total_checked': 0,
        'total_forwarded': 0,
        'by_type': {'new_app': 0, 'ban': 0, 'update': 0, 'bundle': 0, 'other': 0},
        'by_bot': {}
    }
    
    # Обрабатываем каждого бота
    for bot_username in COMPETITOR_BOTS:
        try:
            print(f"\n🤖 Обрабатываю бота: @{bot_username}")
            
            # Получаем entity бота
            bot = await client.get_entity(bot_username)
            
            # Счетчики для текущего бота
            bot_messages = 0
            bot_forwarded = 0
            
            # Загружаем историю
            async for message in client.iter_messages(bot, offset_date=date_from, reverse=True):
                bot_messages += 1
                stats['total_checked'] += 1
                
                # Проверяем дату
                if message.date.replace(tzinfo=None) < date_from:
                    continue
                
                # СПЕЦИАЛЬНАЯ ОБРАБОТКА ДЛЯ BANDA - как в рабочем debug скрипте
                if bot_username == 'banda_rent_apps_bot':
                    if not message.text:
                        continue
                    
                    # Определяем тип сообщения и пересылаем нужные
                    should_forward = False
                    msg_type = None
                    
                    if '🎉 New Android App 🎉' in message.text:
                        should_forward = True
                        msg_type = 'new_app'
                    elif 'BANNED' in message.text and '‼️' in message.text:
                        should_forward = True
                        # Проверяем, есть ли redirect
                        if 'traffic was redirected to' in message.text:
                            msg_type = 'redirect'
                        else:
                        msg_type = 'ban'
                    elif '🎉 New iOS App 🎉' in message.text:
                        # iOS пропускаем
                        continue
                    else:
                        # Остальное тоже пропускаем
                        continue
                    
                    # Пересылаем если нужно
                    if should_forward:
                        try:
                            # Парсим сообщение
                            parsed_data = parse_message_by_bot(message, 'banda_rent_apps_bot')
                            
                            if parsed_data:
                                # Создаем единообразно отформатированное сообщение
                                forward_text = format_unified_message(
                                    parsed_data, 
                                    'banda_rent_apps_bot', 
                                    'Banda Apps', 
                                    message.date, 
                                    message.text
                                )
                                
                                # Отправляем в канал
                                await client.send_message(my_channel, forward_text)
                                bot_forwarded += 1
                                stats['total_forwarded'] += 1
                                stats['by_type'][msg_type] += 1
                                
                                # Прогресс
                                print(f"  📤 Banda {msg_type}: {bot_forwarded} сообщений", end='\r')
                                
                                # Задержка
                                await asyncio.sleep(DELAY_BETWEEN_MESSAGES)
                                
                        except Exception as e:
                            error_msg = str(e)
                            if "wait of" in error_msg and "seconds is required" in error_msg:
                                # Извлекаем время ожидания
                                wait_seconds = int(error_msg.split("wait of ")[1].split(" seconds")[0])
                                print(f"\n  ⏰ Telegram требует подождать {wait_seconds} секунд")
                                await asyncio.sleep(wait_seconds + 5)
                                
                                # Пробуем снова
                                try:
                                    await client.send_message(my_channel, forward_text)
                                    bot_forwarded += 1
                                    stats['total_forwarded'] += 1
                                    stats['by_type'][msg_type] += 1
                                    print(f"  ✅ Успешно отправлено после ожидания")
                                except Exception as retry_error:
                                    print(f"\n  ❌ Повторная ошибка: {retry_error}")
                            else:
                                print(f"\n  ❌ Ошибка при пересылке: {e}")
                    
                    # Переходим к следующему сообщению - banda обработан специально
                    continue
                
                # ДЛЯ ВСЕХ ОСТАЛЬНЫХ БОТОВ - стандартная обработка
                # Проверяем, нужно ли пересылать
                if not should_forward_message(message.text):
                    continue
                
                # Парсим сообщение специфично для каждого бота
                parsed_data = parse_message_by_bot(message, bot_username)
                
                # Если не удалось распарсить или это iOS приложение - пропускаем
                if not parsed_data:
                    continue
                
                # Обновляем тип сообщения
                msg_type = parsed_data['type']
                
                # Проверяем по ключевым словам (дополнительная фильтрация)
                if not should_forward_message(message.text):
                    continue
                
                # Формируем текст для пересылки
                forward_text = format_unified_message(
                    parsed_data,
                    bot_username,
                    bot.first_name,
                    message.date,
                    message.text
                )
                
                try:
                    # Отправляем в канал
                    await client.send_message(my_channel, forward_text)
                    bot_forwarded += 1
                    stats['total_forwarded'] += 1
                    
                    # Обновляем статистику по типам
                    if parsed_data.get('is_bundle'):
                        stats['by_type']['bundle'] += 1
                    else:
                        stats['by_type'][msg_type] += 1
                    
                    # Если есть медиа и включена пересылка медиа
                    if FORWARD_MEDIA and message.media and not message.web_preview:
                        await client.send_file(my_channel, message.media)
                    
                    # Прогресс
                    print(f"  📤 Отфильтровано и переслано: {bot_forwarded} из {bot_messages} проверенных", end='\r')
                    
                    # Задержка
                    await asyncio.sleep(DELAY_BETWEEN_MESSAGES)
                    
                except Exception as e:
                    error_msg = str(e)
                    if "wait of" in error_msg and "seconds is required" in error_msg:
                        # Извлекаем время ожидания
                        wait_seconds = int(error_msg.split("wait of ")[1].split(" seconds")[0])
                        print(f"\n  ⏰ Telegram требует подождать {wait_seconds} секунд (защита от флуда)")
                        print(f"  💤 Жду {wait_seconds + 5} секунд...")
                        await asyncio.sleep(wait_seconds + 5)
                        
                        # Пробуем отправить снова
                        try:
                            await client.send_message(my_channel, forward_text)
                            bot_forwarded += 1
                            stats['total_forwarded'] += 1
                            
                            # Обновляем статистику по типам
                            if parsed_data.get('is_bundle'):
                                stats['by_type']['bundle'] += 1
                            else:
                                stats['by_type'][msg_type] += 1
                                
                            print(f"  ✅ Успешно отправлено после ожидания")
                        except Exception as retry_error:
                            print(f"\n  ❌ Повторная ошибка: {retry_error}")
                            continue
                    else:
                        print(f"\n  ❌ Ошибка при пересылке: {e}")
                        continue
            
            # Сохраняем статистику по боту
            stats['by_bot'][bot_username] = bot_forwarded
            
            print(f"\n  ✅ Проверено сообщений: {bot_messages}")
            print(f"  ✅ Переслано после фильтрации: {bot_forwarded}")
            
        except Exception as e:
            print(f"\n❌ Ошибка с ботом @{bot_username}: {e}")
            stats['by_bot'][bot_username] = 0
            continue
        
        # Пауза между ботами
        if bot_username != COMPETITOR_BOTS[-1]:  # Если не последний бот
            print(f"\n⏳ Пауза перед следующим ботом...")
            await asyncio.sleep(5)
    
    # Итоговая статистика
    print("\n" + "=" * 50)
    print("📊 СТАТИСТИКА ЗАГРУЗКИ:")
    print(f"📨 Всего проверено сообщений: {stats['total_checked']}")
    print(f"✅ Переслано после фильтрации: {stats['total_forwarded']}")
    print(f"\n📈 По типам:")
    print(f"  🚀 Новые приложения: {stats['by_type']['new_app']}")
    print(f"  ❌ Баны: {stats['by_type']['ban']}")
    print(f"  🔄 Обновления: {stats['by_type']['update']}")
    print(f"  📦 Bundle: {stats['by_type']['bundle']}")
    print(f"  📨 Другое: {stats['by_type']['other']}")
    print(f"\n🤖 По ботам:")
    for bot, count in stats['by_bot'].items():
        print(f"  @{bot}: {count} сообщений")
    print(f"\n📍 Проверьте ваш канал для просмотра результатов")

async def main():
    try:
        await load_history()
    except KeyboardInterrupt:
        print("\n\n⚠️ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
    finally:
        await client.disconnect()
        print("\n👋 Отключено от Telegram")

if __name__ == '__main__':
    print("🚀 Загрузчик истории с фильтрацией (FIXED)")
    print("=" * 50)
    asyncio.run(main())