# 🤖 RentBot - Competitor Monitoring System

Advanced Telegram bot for monitoring competitor apps with Google Sheets integration.

## ✨ Features

- **Multi-Bot Monitoring**: Track messages from multiple competitor bots
- **Unified Message Format**: Consistent formatting regardless of source bot
- **Ban Tracking**: Automatic detection and tracking of app bans and redirects
- **Google Sheets Integration**: Real-time synchronization with spreadsheets
- **Bundle Detection**: Special handling for app bundles
- **Geo-Restrictions Tracking**: Monitor geographical limitations
- **OneLink Support**: Track OneLink traffic redirection
- **Real-time Processing**: Efficient message filtering and forwarding

## 🏗️ Architecture

```
RentBot/
├── main.py                    # 🚀 Главное меню приложения
├── config.py                  # ⚙️ Настройки конфигурации
├── load_history_fixed.py      # 📡 Загрузка истории сообщений
├── channel_to_sheets.py       # 📊 Синхронизация с Google Sheets  
├── clean_channel.py           # 🧹 Очистка канала
├── requirements.txt           # 📋 Python зависимости
├── README.md                  # 📖 Документация
├── sessions/                  # 📂 Telegram сессии
│   ├── *.session             # Файлы авторизации
│   └── *.session-journal     # Журналы сессий
├── utils/                     # 📂 Вспомогательные файлы
│   ├── App Examples.txt      # Примеры сообщений
│   └── app_config.json       # Дополнительная конфигурация
├── archive/                   # 📂 Отладочные скрипты
│   └── test_*.py             # Тестовые файлы
└── credentials.json           # 🔑 Google API ключи (создать вручную)
```

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Settings**
   - Edit `config.py` with your Telegram API credentials
   - Set up your channel ID and competitor bot list
   - Configure Google Sheets integration

3. **Setup Google Sheets API**
   - Create credentials.json from Google Cloud Console
   - Enable Google Sheets API
   - Share your spreadsheet with the service account email

4. **Run Application**
   ```bash
   python main.py
   ```

## ⚙️ Configuration

### Telegram API Settings
- `API_ID`: Your Telegram API ID
- `API_HASH`: Your Telegram API hash
- `PHONE`: Your phone number
- `MY_CHANNEL_ID`: Target channel for message forwarding

### Bot Monitoring
- `COMPETITOR_BOTS`: List of competitor bot usernames
- `BOT_PARSERS`: Custom parsing rules for each bot
- `KEYWORDS`: Filter keywords for message relevance

### Google Sheets
- `SPREADSHEET_ID`: Your Google Sheets document ID
- `SHEET_NAME`: Target worksheet name
- `GOOGLE_CREDENTIALS_FILE`: Path to credentials.json

## 📊 Supported Bot Formats

### Banda Apps
- ✅ New Android App announcements
- ✅ Ban notifications with redirect tracking
- ✅ Geo-restrictions parsing
- ✅ OneLink support detection
- ✅ Traffic source information

### WWApps Bot
- ✅ Application releases
- ✅ Bundle detection
- ✅ Category classification

### TDApps Bot
- ✅ New app notifications
- ✅ Ban tracking
- ✅ Package name extraction

## 🔧 Advanced Features

### Message Parsing
Each bot has custom parsing rules defined in `BOT_PARSERS` configuration:
- Pattern matching for different message types
- URL extraction and bundle ID parsing
- Geo-restriction and source tracking
- Redirect chain analysis

### Google Sheets Integration
Automatic data synchronization including:
- App release dates
- Ban dates and status updates
- Lifetime calculations
- Traffic source information
- OneLink support status

### Obfuscation
Code includes obfuscation techniques for production deployment:
- Function name obfuscation
- Variable name encoding
- Entry point masking

## 📈 Usage Examples

### Load Message History
```python
python main.py
# Select option 1: Load message history
```

### Sync with Google Sheets
```python
python main.py
# Select option 3: Synchronize with Google Sheets
```

### Test Configuration
```python
python main.py
# Select option 7: Test mode
```

## 🛡️ Security Features

- Encrypted session storage
- Rate limiting protection
- Error handling and recovery
- Flood protection mechanisms

## 📋 Data Schema

Google Sheets columns:
- **Bot**: Source bot identifier
- **App Name**: Application title
- **Bundle ID**: Android package name
- **Release Date**: First detection date
- **Ban Date**: Ban detection date
- **Lifetime**: Calculated app lifespan
- **Status**: Current app status
- **URL**: Google Play Store link
- **Geo Restrictions**: Geographical limitations
- **Traffic Sources**: Supported traffic sources
- **OneLink**: OneLink support status
- **Redirect Target**: Redirect destination (if banned)

## 🔍 Monitoring Capabilities

- Real-time message processing
- Historical data analysis
- Ban pattern detection
- Traffic redirection tracking
- Performance metrics

## ⚡ Performance

- Optimized for high-volume message processing
- Efficient API usage with rate limiting
- Parallel processing capabilities
- Memory-optimized data structures

## 🤝 Contributing

This is a production system with proprietary enhancements. Contact the development team for collaboration opportunities.

## 📄 License

Proprietary - All rights reserved

---

**Note**: This system is designed for legitimate competitive analysis and monitoring purposes. Ensure compliance with all applicable terms of service and regulations. 