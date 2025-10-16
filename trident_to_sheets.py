from telethon import TelegramClient
from google.oauth2 import service_account
from googleapiclient.discovery import build
from datetime import datetime
import asyncio
import re
from config import *

# Создаем клиент Telegram
client = TelegramClient('sessions/history_session', API_ID, API_HASH)

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
        print(f"❌ Ошибка инициализации Google Sheets: {e}")
        return None

def create_trident_sheet(service):
    """Создает новый лист Trident Apps если его нет"""
    try:
        # Получаем информацию о таблице
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = spreadsheet.get('sheets', [])
        
        # Проверяем есть ли уже лист Trident Apps
        trident_sheet_exists = False
        for sheet in sheets:
            if sheet['properties']['title'] == 'Trident Apps':
                trident_sheet_exists = True
                print("📋 Лист Trident Apps уже существует")
                break
        
        if not trident_sheet_exists:
            # Создаем новый лист
            print("📋 Создаю новый лист Trident Apps...")
            request = {
                'addSheet': {
                    'properties': {
                        'title': 'Trident Apps',
                        'gridProperties': {
                            'rowCount': 1000,
                            'columnCount': 10
                        }
                    }
                }
            }
            
            result = service.spreadsheets().batchUpdate(
                spreadsheetId=SPREADSHEET_ID,
                body={'requests': [request]}
            ).execute()
            
            print("✅ Лист Trident Apps создан")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка создания листа: {e}")
        return False

def parse_message_data(text):
    """Парсит данные из сообщения канала для Trident"""
    data = {}
    
    if not text:
        return data
    
    # Очищаем текст от лишних символов
    clean_text = text.replace('*', '').strip()
    
    # Извлекаем данные о боте
    bot_match = re.search(r'🤖\s*Бот:\s*(.+?)(?:\n|$)', clean_text)
    if bot_match:
        data['bot'] = bot_match.group(1).strip()
    
    # Извлекаем время
    time_match = re.search(r'📅\s*Время:\s*(.+?)(?:\n|$)', clean_text)
    if time_match:
        data['timestamp'] = time_match.group(1).strip()
    
    # Извлекаем тип
    type_match = re.search(r'🏷️\s*Тип:\s*(.+?)(?:\n|$)', clean_text)
    if type_match:
        type_str = type_match.group(1).strip()
        data['type'] = type_str
    
    # Извлекаем название приложения
    app_match = re.search(r'📱\s*(?:\*\*)?Приложение:(?:\*\*)?\s*(.+?)(?:\n|$)', clean_text)
    if not app_match:
        app_match = re.search(r'📱\s*(?:\*\*)?Забанено:(?:\*\*)?\s*(.+?)(?:\n|$)', clean_text)
    if app_match:
        data['app_name'] = clean_app_name(app_match.group(1).strip())
    
    # Извлекаем Bundle ID
    bundle_match = re.search(r'📦\s*Bundle ID:\s*(.+?)(?:\n|$)', clean_text)
    if bundle_match:
        data['bundle_id'] = bundle_match.group(1).strip()
    
    # Извлекаем URL
    url_match = re.search(r'🔗\s*Ссылка:\s*(https?://[^\s]+)', clean_text)
    if url_match:
        data['url'] = url_match.group(1).strip()
    
    # Извлекаем ID сообщения
    msg_id_match = re.search(r'📨\s*ID сообщения:\s*(\d+)', clean_text)
    if msg_id_match:
        data['message_id'] = msg_id_match.group(1).strip()
    
    return data

async def get_trident_from_channel():
    """Получает все приложения Trident из канала"""
    await client.start()
    
    try:
        channel = await client.get_entity(MY_CHANNEL_ID)
        print(f"📨 Анализирую канал: {channel.title}")
        
        apps = {}
        message_count = 0
        parsed_count = 0
        
        # Собираем все сообщения
        messages = []
        async for message in client.iter_messages(channel):
            if message.text and ('🤖' in message.text and 'Бот:' in message.text) and ('Trident' in message.text or 'trident_appbot' in message.text):
                messages.append(message)
                message_count += 1
        
        # Обрабатываем сообщения от старых к новым
        messages.reverse()
        
        for message in messages:
            data = parse_message_data(message.text)
            
            if not data.get('app_name'):
                continue
                
            parsed_count += 1
            
            # Создаем ключ приложения
            app_key = (data.get('bot', ''), data['app_name'], data.get('bundle_id', ''))
            
            if data.get('type') == 'new_app':
                # Новое приложение
                apps[app_key] = {
                    'bot': data.get('bot', 'Trident Apps'),
                    'app_name': data['app_name'],
                    'bundle_id': data.get('bundle_id', ''),
                    'release_date': data.get('timestamp', ''),
                    'ban_date': '',
                    'status': 'Активно',
                    'url': data.get('url', ''),
                    'message_id': data.get('message_id', '')
                }
            
            elif data.get('type') == 'ban':
                # Ищем соответствующее приложение для бана
                banned_app_name = data['app_name']
                
                for key, app_data in apps.items():
                    if app_data['app_name'] == banned_app_name:
                        print(f"✅ НАЙДЕН И ОБНОВЛЕН БАН для: {banned_app_name}")
                        app_data['ban_date'] = data.get('timestamp', '')
                        app_data['status'] = 'Забанено'
                        break
                else:
                    print(f"⚠️ НЕ НАЙДЕНО приложение для бана: {banned_app_name}")
                    # Создаем новую запись для забаненного приложения
                    apps[app_key] = {
                        'bot': data.get('bot', 'Trident Apps'),
                        'app_name': data['app_name'],
                        'bundle_id': data.get('bundle_id', ''),
                        'release_date': '',
                        'ban_date': data.get('timestamp', ''),
                        'status': 'Забанено (без истории выхода)',
                        'url': data.get('url', ''),
                        'message_id': data.get('message_id', '')
                    }
            
            # Прогресс
            if parsed_count % 10 == 0:
                print(f"  Обработано сообщений: {parsed_count}", end='\r')
        
        print(f"\n✅ Обработано сообщений: {message_count}")
        print(f"📄 Успешно распарсено: {parsed_count}")
        print(f"📱 Найдено уникальных приложений Trident: {len(apps)}")
        
        return list(apps.values())
        
    finally:
        await client.disconnect()

def convert_date_for_sheets(date_str):
    """Конвертирует дату из формата DD.MM.YYYY HH:MM в формат DD.MM.YYYY для отображения"""
    if not date_str or date_str == '':
        return ''
    
    try:
        if ' ' in date_str:
            date_str = date_str.split(' ')[0]  # Убираем время, оставляем только дату
        return date_str
    except:
        return date_str

def prepare_sheets_data(apps):
    """Подготавливает данные для Google Sheets"""
    rows = []
    
    # Заголовки
    headers = [
        'Бот', 'Название приложения', 'Bundle ID', 'Дата выхода', 'Дата бана', 
        'Срок жизни (дни)', 'Статус', 'URL', 'ID сообщения'
    ]
    rows.append(headers)
    
    for app in apps:
        # Простая формула: Дата бана - Дата выхода
        row_number = len(rows) + 1  # Номер текущей строки
        lifetime_formula = f'=IF(E{row_number}="", "", E{row_number}-D{row_number})'
        
        row = [
            app['bot'],                                    # A: Бот
            app['app_name'],                               # B: Название приложения
            app.get('bundle_id', ''),                      # C: Bundle ID
            convert_date_for_sheets(app['release_date']),  # D: Дата выхода
            convert_date_for_sheets(app['ban_date']),      # E: Дата бана
            lifetime_formula,                              # F: Срок жизни (формула)
            app['status'],                                 # G: Статус
            app['url'],                                    # H: URL
            str(app['message_id'])                         # I: ID сообщения
        ]
        rows.append(row)
    
    return rows

def update_trident_sheet(service, data):
    """Обновляет данные в листе Trident Apps"""
    try:
        # Очищаем лист Trident Apps
        print("🧹 Очищаю старые данные в листе Trident Apps...")
        service.spreadsheets().values().clear(
            spreadsheetId=SPREADSHEET_ID,
            range='Trident Apps!A:Z'
        ).execute()
        
        # Записываем новые данные
        print(f"📝 Записываю {len(data)} строк в лист Trident Apps...")
        body = {
            'values': data,
            'majorDimension': 'ROWS'
        }
        
        result = service.spreadsheets().values().update(
            spreadsheetId=SPREADSHEET_ID,
            range='Trident Apps!A1',
            valueInputOption='USER_ENTERED',  # Позволяет использовать формулы
            body=body
        ).execute()
        
        print(f"✅ Обновлено {result.get('updatedRows', 0)} строк в листе Trident Apps")
        
        # Форматируем таблицу
        format_requests = [
            # Автоматическая ширина колонок
            {
                "autoResizeDimensions": {
                    "dimensions": {
                        "sheetId": get_sheet_id(service, 'Trident Apps'),
                        "dimension": "COLUMNS",
                        "startIndex": 0,
                        "endIndex": 9
                    }
                }
            }
        ]
        
        service.spreadsheets().batchUpdate(
            spreadsheetId=SPREADSHEET_ID,
            body={"requests": format_requests}
        ).execute()
        
        print("✅ Лист Trident Apps отформатирован")
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении листа Trident Apps: {e}")

def get_sheet_id(service, sheet_name):
    """Получает ID листа по названию"""
    try:
        spreadsheet = service.spreadsheets().get(spreadsheetId=SPREADSHEET_ID).execute()
        sheets = spreadsheet.get('sheets', [])
        
        for sheet in sheets:
            if sheet['properties']['title'] == sheet_name:
                return sheet['properties']['sheetId']
        return 0  # Возвращаем 0 если не найдено
    except:
        return 0

async def main():
    try:
        # Получаем данные Trident из канала
        apps = await get_trident_from_channel()
        
        # Статистика
        print("\n📊 Статистика Trident Apps:")
        bundle_count = sum(1 for app in apps if app.get('bundle_id'))
        banned_count = sum(1 for app in apps if 'Забанено' in app['status'])
        
        print(f"📱 Всего приложений: {len(apps)}")
        print(f"📦 С Bundle ID: {bundle_count}")
        print(f"❌ Забанено: {banned_count}")
        
        # Инициализируем Google Sheets
        print("\n📊 Обновляю Google Sheets...")
        service = init_google_sheets()
        if not service:
            return
        
        # Создаем лист Trident Apps если нужно
        if not create_trident_sheet(service):
            return
        
        # Подготавливаем данные
        sheets_data = prepare_sheets_data(apps)
        
        # Обновляем лист Trident Apps
        update_trident_sheet(service, sheets_data)
        
        print("\n✅ Готово! Проверьте лист Trident Apps в вашей таблице")
        print(f"🔗 {SPREADSHEET_URL}")
        
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")

if __name__ == "__main__":
    print("🔱 Синхронизация Trident Apps с Google Sheets")
    print("=" * 50)
    asyncio.run(main()) 