from telethon import TelegramClient
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import asyncio
import re
from config import *

# Создаем клиент Telegram
client = TelegramClient('sheets_session', API_ID, API_HASH)

# Настройка Google Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

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

def init_google_sheets():
    """Инициализация Google Sheets API"""
    try:
        creds = service_account.Credentials.from_service_account_file(
            GOOGLE_CREDENTIALS_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)
        return service
    except Exception as e:
        print(f"❌ Ошибка при подключении к Google Sheets: {e}")
        print("Проверьте файл credentials.json и SPREADSHEET_ID в config.py")
        return None

def extract_bundle_from_url(url):
    """Извлекает bundle ID из URL Google Play"""
    if not url:
        return None
    
    # Паттерн для Google Play URL
    match = re.search(r'id=([^\s&]+)', url)
    if match:
        return match.group(1)
    return None

def parse_message_data(text):
    """Извлекает данные из форматированного сообщения"""
    data = {
        'bot': None,
        'app_name': None,
        'is_bundle': False,
        'date': None,
        'type': None,
        'url': None,
        'message_id': None,
        'bundle_id': None,
        'bot_username': None,  # Добавляем для хранения @username
        'geo_restrictions': None,
        'sources': None,
        'has_onelink': False,
        'has_macro_system': False,
        'redirect_to': None,
        'original_app': None
    }
    
    if not text:
        return data
    
    # Убираем лишние звездочки из текста для упрощения парсинга
    clean_text = text.replace('**', '')
    
    # Извлекаем username бота из "История от" или "Новое от"
    username_match = re.search(r'История от\s*@(\w+)', clean_text)
    if not username_match:
        username_match = re.search(r'Новое от\s*@(\w+)', clean_text)
    if username_match:
        data['bot_username'] = '@' + username_match.group(1)
    
    # Извлекаем имя бота из поля "🤖 Бот:"
    bot_name_match = re.search(r'🤖\s*Бот:\s*(.+?)(?:\n|$)', clean_text)
    if bot_name_match:
        data['bot'] = bot_name_match.group(1).strip()
    else:
        # Если не нашли поле "🤖 Бот:", используем username
        data['bot'] = data['bot_username']
    
    # Извлекаем дату и время
    date_match = re.search(r'📅\s*Время:\s*(.+?)(?:\n|$)', clean_text)
    if date_match:
        data['date'] = date_match.group(1).strip()
    
    # Извлекаем тип
    type_match = re.search(r'🏷️\s*Тип:\s*(.+?)(?:\n|$)', clean_text)
    if type_match:
        type_str = type_match.group(1).strip()
        data['type'] = type_str
    
    # Извлекаем название приложения (разные поля в зависимости от типа)
    app_match = re.search(r'📱\s*(?:\*\*)?Приложение:(?:\*\*)?\s*(.+?)(?:\n|$)', clean_text)
    if not app_match:
        app_match = re.search(r'📱\s*(?:\*\*)?Забанено:(?:\*\*)?\s*(.+?)(?:\n|$)', clean_text)
    if app_match:
        data['app_name'] = clean_app_name(app_match.group(1).strip())
    
    # Для редиректов - извлекаем оригинальное и новое приложение
    if data['type'] == 'redirect':
        original_match = re.search(r'❌\s*Забанено:\s*(.+?)(?:\n|$)', clean_text)
        if original_match:
            data['original_app'] = clean_app_name(original_match.group(1).strip())
        
        redirect_match = re.search(r'🔄\s*Перенаправлено на:\s*(.+?)(?:\n|$)', clean_text)
        if redirect_match:
            data['redirect_to'] = clean_app_name(redirect_match.group(1).strip())
            # Для редиректов используем новое приложение как основное название
            data['app_name'] = data['redirect_to']
    
    # Извлекаем Bundle ID
    bundle_match = re.search(r'📦\s*Bundle ID:\s*(.+?)(?:\n|$)', clean_text)
    if bundle_match:
        data['bundle_id'] = bundle_match.group(1).strip()
    
    # Извлекаем дополнительную информацию для Banda Apps
    geo_match = re.search(r'🌍\s*Гео-ограничения:\s*(.+?)(?:\n|$)', clean_text)
    if geo_match:
        data['geo_restrictions'] = geo_match.group(1).strip()
    
    sources_match = re.search(r'📊\s*Источники:\s*(.+?)(?:\n|$)', clean_text)
    if sources_match:
        data['sources'] = sources_match.group(1).strip()
    
    # Проверяем наличие OneLink и автосбора макросов
    data['has_onelink'] = bool(re.search(r'🔗\s*OneLink:\s*Поддерживается', clean_text))
    data['has_macro_system'] = bool(re.search(r'🤖\s*Автосбор макросов:\s*Есть', clean_text))
    
    # Извлекаем URL
    url_match = re.search(r'🔗\s*Ссылка:\s*(.+?)(?:\n|$)', clean_text)
    if url_match:
        data['url'] = url_match.group(1).strip()
    else:
        # Пробуем найти URL в тексте
        url_pattern = r'https?://[^\s\)]+'
        url_found = re.search(url_pattern, text)
        if url_found:
            data['url'] = url_found.group(0)
    
    return data

async def get_all_apps_from_channel():
    """Получает все приложения из канала"""
    await client.start(PHONE)
    print("✅ Подключено к Telegram")
    
    # Получаем канал
    channel = await client.get_entity(MY_CHANNEL_ID)
    print(f"📨 Читаю сообщения из канала: {channel.title}")
    
    # Словарь для хранения приложений
    # Ключ теперь включает полное название и bundle для точной идентификации
    apps = {}
    
    # Читаем все сообщения
    message_count = 0
    parsed_count = 0
    
    # Сначала собираем ВСЕ сообщения
    all_messages = []
    async for message in client.iter_messages(channel, limit=None):
        all_messages.append(message)
    
    # Обрабатываем в обратном порядке (от старых к новым)
    all_messages.reverse()
    
    for message in all_messages:
        if not message.text:
            continue
            
        message_count += 1
        
        # Парсим данные
        data = parse_message_data(message.text)
        data['message_id'] = message.id
        
        if not data['bot'] or not data['app_name']:
            continue
        
        parsed_count += 1
        
        # Используем bundle_id если он есть, иначе пытаемся извлечь из URL
        if data.get('bundle_id'):
            bundle = data['bundle_id']
        elif data.get('url'):
            bundle = extract_bundle_from_url(data['url'])
        else:
            bundle = None
        
        # Ключ для идентификации приложения
        # Используем полное название + bundle (если есть) для уникальности
        if bundle:
            app_key = (data['bot'], data['app_name'], bundle)
        else:
            app_key = (data['bot'], data['app_name'], 'no_bundle')
        
        # Определяем, это выход или бан
        if data['type'] and ('ban' in data['type'].lower() or 'redirect' in data['type'].lower()):
            # Это сообщение о бане или редиректе
            found = False
            
            # Для отладки
            print(f"\n🔍 Обработка бана/редиректа:")
            print(f"   Тип: {data['type']}")
            print(f"   Бот: {data['bot']}")
            print(f"   Username: {data.get('bot_username', 'не найден')}")
            print(f"   Приложение: {data['app_name']}")
            print(f"   Оригинальное (для redirect): {data.get('original_app', 'нет')}")
            print(f"   Bundle: {bundle}")
            
            # Для редиректов нужно искать оригинальное приложение
            search_name = data.get('original_app') if data['type'] == 'redirect' else data['app_name']
            
            # Улучшенный поиск приложения
            for app_key, app_data in list(apps.items()):
                # Проверяем совпадение бота  
                bot_match = False
                
                # Проверяем точное совпадение бота
                if bots_match(app_data['bot'], data['bot']) or (data.get('bot_username') and bots_match(app_data['bot'], data['bot_username'])):
                    bot_match = True
                # Проверяем совпадение по username
                elif data.get('bot_username') and app_data['bot'] == data['bot_username']:
                    bot_match = True
                # Проверяем частичное совпадение (для случаев типа "Banda Apps" и "@banda_rent_apps_bot")
                elif data['bot'] and app_data['bot'] and (data['bot'].lower() in app_data['bot'].lower() or app_data['bot'].lower() in data['bot'].lower()):
                    bot_match = True
                
                if not bot_match:
                    continue
                
                # Улучшенная проверка совпадения приложения
                app_match = False
                app_name_in_db = app_data['app_name']
                
                # 1. Точное совпадение по названию
                if search_name and app_name_in_db == search_name:
                    app_match = True
                    print(f"   ✅ Точное совпадение: '{search_name}'")
                
                # 2. Нормализованное совпадение (убираем регистр и пробелы)
                elif search_name and app_name_in_db.lower().strip() == search_name.lower().strip():
                    app_match = True
                    print(f"   ✅ Нормализованное совпадение: '{search_name}'")
                
                # 3. Совпадение с удалением эмодзи и специальных символов
                elif search_name and app_name_in_db:
                    # Очищаем названия от эмодзи и спецсимволов
                    clean_search = re.sub(r'[^\w\s]', '', search_name).strip().lower()
                    clean_db = re.sub(r'[^\w\s]', '', app_name_in_db).strip().lower()
                    
                    if clean_search == clean_db:
                        app_match = True
                        print(f"   ✅ Совпадение после очистки: '{search_name}'")
                
                # 4. Частичное совпадение для случаев с небольшими различиями
                elif search_name and app_name_in_db:
                    # Убираем пробелы и сравниваем
                    search_compact = search_name.replace(' ', '').lower()
                    db_compact = app_name_in_db.replace(' ', '').lower()
                    
                    if search_compact == db_compact:
                    app_match = True
                        print(f"   ✅ Совпадение без пробелов: '{search_name}'")
                
                if app_match:
                    # Обновляем информацию о бане
                    apps[app_key]['ban_date'] = data['date']
                    apps[app_key]['status'] = 'Забанено'
                    
                    # Для редиректов добавляем информацию о перенаправлении
                    if data['type'] == 'redirect' and data.get('redirect_to'):
                        apps[app_key]['redirect_to'] = data['redirect_to']
                        apps[app_key]['status'] = f"Забанено → {data['redirect_to']}"
                    
                    found = True
                    print(f"   ✅ НАЙДЕН И ОБНОВЛЕН БАН для: {app_data['app_name']}")
                    print(f"   📅 Дата бана: {data['date']}")
                    print(f"   📊 Новый статус: {apps[app_key]['status']}")
                    break
            
            if not found:
                print(f"   ⚠️ НЕ НАЙДЕНО приложение для бана/редиректа")
                print(f"   🔍 Ищем по названию: '{search_name}'")
                print(f"   📦 Bundle: '{bundle}'")
                print(f"   📋 Существующие приложения от этого бота:")
                
                # Показываем только приложения от того же бота
                bot_apps = []
                for app_key, app_data in apps.items():
                    if (data['bot'] and data['bot'].lower() in app_data['bot'].lower()) or \
                       (data.get('bot_username') and data['bot_username'] in app_data['bot']):
                        bot_apps.append((app_data['app_name'], app_data.get('bundle_id', 'no_bundle')))
                
                # Сортируем и показываем только первые 10 для читаемости
                bot_apps.sort()
                for i, (name, bundle_id) in enumerate(bot_apps[:10]):
                    print(f"     {i+1}. {name} ({bundle_id})")
                
                if len(bot_apps) > 10:
                    print(f"     ... и еще {len(bot_apps) - 10} приложений")
        else:
            # Это сообщение о выходе приложения
            # Используем имя бота если есть, иначе username
            bot_identifier = data['bot'] if data['bot'] else data.get('bot_username', 'unknown')
            
            # Создаем простой ключ без tuple
            app_key = f"{bot_identifier}_{data['app_name']}"
            
            if app_key not in apps:
                apps[app_key] = {
                    'bot': bot_identifier,
                    'app_name': data['app_name'],
                    'is_bundle': data['is_bundle'],
                    'bundle_id': bundle or '',
                    'release_date': data['date'],
                    'ban_date': '',
                    'status': 'Активно',
                    'url': data['url'] or '',
                    'message_id': data['message_id'],
                    'geo_restrictions': data.get('geo_restrictions', ''),
                    'sources': data.get('sources', ''),
                    'has_onelink': data.get('has_onelink', False),
                    'has_macro_system': data.get('has_macro_system', False),
                    'redirect_to': ''
                }
        
        # Прогресс
        if message_count % 10 == 0:
            print(f"  Обработано сообщений: {message_count}", end='\r')
    
    print(f"\n✅ Обработано сообщений: {message_count}")
    print(f"📄 Успешно распарсено: {parsed_count}")
    print(f"📱 Найдено уникальных приложений: {len(apps)}")
    
    # Отладочная информация если ничего не найдено
    if len(apps) == 0 and message_count > 0:
        print("\n📊 Отладочная информация:")
        
        # Показываем последние сообщения для отладки
        print(f"\nПоследние 3 сообщения в канале:")
        msg_num = 0
        async for message in client.iter_messages(channel, limit=3):
            if message.text:
                msg_num += 1
                print(f"\n--- Сообщение {msg_num} ---")
                print(message.text[:300] + "..." if len(message.text) > 300 else message.text)
                
                # Пробуем распарсить
                test_data = parse_message_data(message.text)
                print(f"\nРезультат парсинга:")
                for key, value in test_data.items():
                    if value:
                        print(f"  {key}: {value}")
    
    return list(apps.values())

def convert_date_for_sheets(date_str):
    """Конвертирует дату из формата DD.MM.YYYY HH:MM в формат DD.MM.YYYY для отображения"""
    if not date_str or date_str == '':
        return ''
    
    try:
        # Парсим дату в формате DD.MM.YYYY HH:MM
        if ' ' in date_str:
            date_str = date_str.split(' ')[0]  # Убираем время, оставляем только дату
        
        # Возвращаем в том же формате DD.MM.YYYY
        return date_str
    except:
        return date_str  # Если не удалось конвертировать, возвращаем как есть

def prepare_sheets_data(apps):
    """Подготавливает данные для Google Sheets"""
    rows = []
    
    for app in apps:
        # Простая формула: Дата бана - Дата выхода
        row_number = len(rows) + 2  # Номер текущей строки
        # Простое вычитание дат (Google Sheets автоматически распознает формат DD.MM.YYYY)
        lifetime_formula = f'=IF(E{row_number}="", "", E{row_number}-D{row_number})'
        
        row = [
            app['bot'],                              # A: Бот
            app['app_name'],                         # B: Название приложения
            app.get('bundle_id', ''),                # C: Bundle ID
            convert_date_for_sheets(app['release_date']),  # D: Дата выхода (конвертированная)
            convert_date_for_sheets(app['ban_date']),      # E: Дата бана (конвертированная)
            lifetime_formula,                        # F: Срок жизни (формула)
            app['status'],                           # G: Статус
            app['url'],                              # H: URL
            str(app['message_id']),                  # I: ID сообщения
            app.get('geo_restrictions', ''),         # J: Гео-ограничения
            app.get('sources', ''),                  # K: Источники трафика
            'Да' if app.get('has_onelink', False) else 'Нет',  # L: OneLink
            'Да' if app.get('has_macro_system', False) else 'Нет',  # M: Автосбор макросов
            app.get('redirect_to', '')               # N: Перенаправлено на
        ]
        rows.append(row)
    
    # Сортируем по боту и дате выхода
    rows.sort(key=lambda x: (x[0], x[3]), reverse=True)
    
    return rows

async def update_google_sheets(apps):
    """Обновляет Google Sheets"""
    service = init_google_sheets()
    if not service:
        return
    
    try:
        # Подготавливаем данные
        rows = prepare_sheets_data(apps)
        
        if not rows:
            print("⚠️ Нет данных для записи")
            return
        
        # Очищаем существующие данные (кроме заголовков)
        print("🧹 Очищаю старые данные...")
        service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE
        ).execute()
        
        # Записываем новые данные
        print(f"📝 Записываю {len(rows)} строк...")
        body = {
            'values': rows,
            'majorDimension': 'ROWS'
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range=SHEET_RANGE,
            valueInputOption='USER_ENTERED',  # Позволяет использовать формулы
            body=body
        ).execute()
        
        print(f"✅ Обновлено {result.get('updatedRows', 0)} строк")
        
        # Форматируем таблицу
        format_requests = [
            # Автоматическая ширина колонок (расширяем до 14 колонок)
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": 0,
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 14
                    }
                }
            }
        ]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": format_requests}
        ).execute()
        
        print("✅ Таблица отформатирована")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении таблицы: {e}")

async def main():
    try:
        # Получаем данные из канала
        apps = await get_all_apps_from_channel()
        
        # Статистика
        print("\n📊 Статистика:")
        bots_stats = {}
        bundle_count = 0
        banned_count = 0
        
        for app in apps:
            bot = app['bot']
            if bot not in bots_stats:
                bots_stats[bot] = {'total': 0, 'banned': 0, 'bundle': 0}
            
            bots_stats[bot]['total'] += 1
            if app['is_bundle']:
                bundle_count += 1
                bots_stats[bot]['bundle'] += 1
            if app['status'] == 'Забанено':
                banned_count += 1
                bots_stats[bot]['banned'] += 1
        
        print(f"📱 Всего приложений: {len(apps)}")
        print(f"📦 Bundle: {bundle_count}")
        print(f"❌ Забанено: {banned_count}")
        print(f"\n🤖 По ботам:")
        for bot, stats in bots_stats.items():
            print(f"  {bot}: {stats['total']} приложений ({stats['bundle']} bundle, {stats['banned']} забанено)")
        
        # Обновляем Google Sheets
        if apps:
            print("\n📊 Обновляю Google Sheets...")
            await update_google_sheets(apps)
            print(f"\n✅ Готово! Проверьте вашу таблицу")
            print(f"🔗 https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}")
        
    except Exception as e:
        print(f"❌ Критическая ошибка: {e}")
    finally:
        await client.disconnect()
        
def bots_match(bot1, bot2):
    """Проверяет, относятся ли два идентификатора к одному боту"""
    if not bot1 or not bot2:
        return False
    
    # Приводим к нижнему регистру для сравнения
    bot1_lower = bot1.lower()
    bot2_lower = bot2.lower()
    
    # Точное совпадение
    if bot1_lower == bot2_lower:
        return True
    
    # Убираем @ для сравнения
    bot1_clean = bot1_lower.replace('@', '').replace('_bot', '').replace('bot', '')
    bot2_clean = bot2_lower.replace('@', '').replace('_bot', '').replace('bot', '')
    
    # Проверяем совпадение очищенных версий
    if bot1_clean == bot2_clean:
        return True
    
    # Проверяем, содержится ли одно в другом
    if bot1_clean in bot2_clean or bot2_clean in bot1_clean:
        return True
    
    # Специальные случаи для известных ботов
    known_mappings = {
        'banda': ['banda_rent_apps_bot', 'banda apps'],
        'ww': ['wwapps_bot', 'ww apps'],
        # Добавьте другие известные соответствия
    }
    
    for key, values in known_mappings.items():
        if any(key in b.lower() for b in [bot1, bot2]):
            if any(v in bot1_lower for v in values) and any(v in bot2_lower for v in values):
                return True
    
    return False


if __name__ == '__main__':
    print("📊 Перенос данных из Telegram в Google Sheets")
    print("=" * 50)
    asyncio.run(main())
    
# Добавьте эту функцию в channel_to_sheets.py

def normalize_app_name(name):
    """Нормализует название приложения для сопоставления"""
    if not name:
        return ""
    
    # Убираем эмодзи
    name = re.sub(r'[^\w\s\-\:]', '', name)
    
    # Убираем лишние пробелы
    name = ' '.join(name.split())
    
    # Приводим к нижнему регистру
    name = name.lower()
    
    # Убираем числа в конце (new 57, 16+)
    name = re.sub(r'\s*\d+\s*$', '', name)
    name = re.sub(r'\s+new\s+\d+', '', name)
    
    # Убираем общие слова
    name = name.replace(' new ', ' ')
    name = name.replace(' td', '')
    
    return name.strip()

