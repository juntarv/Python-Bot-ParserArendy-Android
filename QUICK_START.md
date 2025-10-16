# 🚀 Быстрые команды RentBot

## 📋 Основные команды

### 🔄 Сбор данных
```bash
# Собрать все сообщения от ботов
python load_history_fixed.py

# Очистить канал перед новым сбором
python clean_channel.py
```

### 📊 Синхронизация с Google Sheets
```bash
# Все боты сразу
python channel_to_sheets.py

# Отдельные боты
python banda_to_sheets.py      # Banda Apps
python wwapps_to_sheets.py     # WWApps  
python trident_to_sheets.py    # Trident Apps
```

## ⚙️ Настройка (config.py)

### 1. Telegram API
```python
API_ID = 12345678
API_HASH = 'your_hash'
MY_CHANNEL_ID = -1001234567890
```

### 2. Google Sheets
```python
GOOGLE_CREDENTIALS_FILE = 'credentials.json'
SPREADSHEET_ID = 'your_spreadsheet_id'
```

### 3. Боты (убрать # для активации)
```python
COMPETITOR_BOTS = [
    'banda_rent_apps_bot',    # Banda Apps
    'wwapps_bot',             # WWApps
    'trident_appbot',         # Trident Apps
]
```

## 📈 Результат

- **Telegram канал**: Единый формат сообщений
- **Google Sheets**: Отдельные листы по ботам
- **Статистика**: Автоматический расчет срока жизни приложений
