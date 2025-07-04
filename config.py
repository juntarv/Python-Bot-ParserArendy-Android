# config.py - Все настройки в одном месте

# ========== TELEGRAM API ==========
API_ID = 21300389  # Ваш api_id (число без кавычек)
API_HASH = 'acf2f54b7dd38ae4ca633427f7d7f32c'  # Ваш api_hash (в кавычках)
PHONE = '+380962820343'  # Ваш номер телефона

# ========== КАНАЛЫ ==========
MY_CHANNEL_ID = -1002568412343  # ID вашего канала для пересылки



# ========== БОТЫ КОНКУРЕНТОВ ==========
COMPETITOR_BOTS = [
    'banda_rent_apps_bot',
    'wwapps_bot',
    'td_appsbot',
    # Добавьте сюда всех ботов
]
# ========== ПАРСЕРЫ ДЛЯ КАЖДОГО БОТА ==========
# Настройки парсинга для каждого бота
BOT_PARSERS = {
    'wwapps_bot': {
        'new_app_patterns': [r'‼️ Доступно новое приложение ‼️'],
        'ban_patterns': [r'‼️ BAN ‼️'],
        'skip_patterns': ['iOS платформа', 'Платформа: iOS'],
        'name_pattern': r'Название:\s*(.+?)(?:\n|$)',
        'bundle_pattern': r'Bundle:\s*([^\s\n]+)',
        'url_in_name': True,  # URL встроен в название
        'category_pattern': r'Категория:\s*(.+?)(?:\n|$)'
    },
    
    'banda_rent_apps_bot': {
        'new_app_patterns': [r'🎉 New Android App 🎉'],
        'ban_patterns': [r'BANNED', r'‼️ Application .+ BANNED ‼️'],
        'skip_patterns': ['New iOS App', '🎉 New iOS App 🎉'],
        'name_pattern': r'🎉 New Android App 🎉\s*\n\s*(.+?)(?:\n|$)',  # Название на следующей строке с пробелами
        'ban_name_pattern': r'Application\s+(.+?)\s+BANNED',  # Для банов
        'bundle_pattern': None,  # У них нет bundle в тексте
        'url_in_ban': True,  # URL есть в сообщениях о бане
        'extract_bundle_from_url': True  # Извлекать bundle из URL
    },
    
    'td_appsbot': {
        'new_app_patterns': [r'Добавлено новое приложение', r'🟢 FREE 🟢'],
        'ban_patterns': [r'‼️ BAN ‼️'],
        'skip_patterns': [],
        'name_pattern': r'Название приложения:\s*(.+?)(?:\n|$)',
        'bundle_pattern': r'Имя пакета:\s*([^\s\n]+)',
        'url_pattern': r'https://play\.google\.com/store/apps/details\?id=([^\s&]+)',
        'ban_name_pattern': r'TDApps \| (.+?)(?:\n|$)'  # Особый паттерн для имени в бане
    }
}

# ========== КЛЮЧЕВЫЕ СЛОВА ДЛЯ ФИЛЬТРАЦИИ ==========
# Сообщения будут пересланы только если содержат эти слова
KEYWORDS = {
    'new_app': [
        # Русские варианты
        'вышло', 'вышел', 'вышла',
        'запустили', 'запустил', 'запуск',
        'новое приложение', 'новый апп', 'новая игра',
        'релиз', 'released', 'launch',
        'теперь доступно', 'уже в сторе',
        'появилось', 'добавили',
        'опубликовали', 'опубликовано',
        'залили', 'выложили',
        
        # Английские варианты  
        'new app', 'new game', 'launched',
        'now available', 'just released',
        'published', 'live now',
        'app store', 'play store',
        'google play', 'appstore'
    ],
    
    'ban': [
        # Русские варианты
        'забанили', 'забанен', 'забанено',
        'удалили', 'удален', 'удалено', 
        'заблокировали', 'заблокирован',
        'бан', 'ban', 'banned',
        'отклонили', 'отклонен', 'rejected',
        'сняли', 'снято с публикации',
        
        # Английские варианты
        'removed', 'deletion', 'suspended',
        'taken down', 'blocked',
        'terminated', 'disabled'
    ],
    
    'update': [
        # Обновления приложений
        'обновили', 'обновление', 'update',
        'апдейт', 'новая версия', 'версия'
    ],
    
    'bundle': [
        # Bundle приложения
        'bundle', 'бандл', 'пакет', 'набор',
        'комплект', 'сборка'
    ]
}

# Объединяем все ключевые слова в один список для поиска
ALL_KEYWORDS = []
for category, words in KEYWORDS.items():
    ALL_KEYWORDS.extend(words)

# ========== НАСТРОЙКИ ЗАГРУЗКИ ИСТОРИИ ==========
DAYS_TO_LOAD = 30  # За сколько дней загружать историю
DELAY_BETWEEN_MESSAGES = 10  # Задержка между сообщениями (секунды)

# ========== НАСТРОЙКИ ФИЛЬТРАЦИИ ==========
# Если True - пересылаются только сообщения с ключевыми словами
# Если False - пересылаются все сообщения
FILTER_BY_KEYWORDS = True

# Минимальная длина сообщения (фильтрует спам)
MIN_MESSAGE_LENGTH = 10

# ========== ФОРМАТИРОВАНИЕ ==========
# Добавлять ли эмодзи к сообщениям
USE_EMOJI = True

# Эмодзи для разных типов сообщений
EMOJI = {
    'new_app': '🚀',
    'ban': '❌',
    'update': '🔄',
    'bundle': '📦',
    'other': '📨'
}

# ========== НАСТРОЙКИ ПЕРЕСЫЛКИ ==========
# Пересылать ли медиа-файлы (фото, видео, документы)
FORWARD_MEDIA = False  # Поставьте True, если хотите пересылать медиа

# ========== GOOGLE SHEETS ==========
# ID вашей Google таблицы (из URL)
SPREADSHEET_ID = '16vssvhkTnjBcY_81ABQJccvP7goDn_GaaOhqekNIenI'  # Вставьте ID из URL таблицы

# Путь к файлу с credentials
GOOGLE_CREDENTIALS_FILE = 'credentials.json'

# Название листа в таблице
SHEET_NAME = 'Мониторинг'  # Или как вы назвали лист

# Диапазон для записи (начальная строка)
SHEET_RANGE = f'{SHEET_NAME}!A2:I'  # Начиная со второй строки (первая - заголовки)