# config.py - Все настройки в одном месте

# ========== TELEGRAM API ==========
API_ID =   # Ваш api_id (число без кавычек)
API_HASH = ''  # Ваш api_hash (в кавычках)
PHONE = '+'  # Ваш номер телефона

# ========== КАНАЛЫ ==========
MY_CHANNEL_ID = -  # ID вашего канала для пересылки



# ========== БОТЫ КОНКУРЕНТОВ ==========
COMPETITOR_BOTS = [
    #'banda_rent_apps_bot',
    #'wwapps_bot',
    'trident_appbot'
    #'td_appsbot',
    # Добавьте сюда всех ботов
]

# ========== ПАРСЕРЫ ДЛЯ КАЖДОГО БОТА ==========
# Настройки парсинга для каждого бота
BOT_PARSERS = {
    'wwapps_bot': {
        'new_app_patterns': [r'‼️ Доступно новое приложение ‼️'],
        'ban_patterns': [r'‼️ BAN ‼️'],
        'skip_patterns': ['iOS платформа', 'Платформа: iOS'],
        'name_pattern': r'Название:\s*(.+?)\*{0,2}\s*\(https',
        'ban_name_pattern': r'Приложение:\s*(.+?)(?:\n|$)',
        'bundle_pattern': r'Bundle:\s*([^\s\n]+)',
        'url_pattern': r'https://play\.google\.com/store/apps/details\?id=([^\s&)]+)',
        'category_pattern': r'Категория:\s*(.+?)(?:\n|$)',
        'geo_pattern': r'Закрытые ГЕО:\s*(.+?)(?:\n|$)',
        'age_pattern': r'Возраст\s*-\s*(.+?)(?:\n|$)',
        'url_in_name': True,  # URL встроен в название
        'extract_bundle_from_url': True
    },
    
    'banda_rent_apps_bot': {
        'new_app_patterns': [
            r'🎉 New Android App 🎉',
            r'🎉\s*New Android App\s*🎉'
        ],
        'ban_patterns': [
            r'BANNED',
            r'‼️ Application .+ BANNED ‼️',
            r'‼️\s*Application\s+.+\s+BANNED\s*‼️'
        ],
        'redirect_patterns': [
            r'To avoid losses, the traffic was redirected to',
            r'traffic was redirected to'
        ],
        'skip_patterns': [
            'New iOS App', 
            '🎉 New iOS App 🎉',
            r'🎉\s*New iOS App\s*🎉'
        ],
        'name_pattern': r'🎉\s*New Android App\s*🎉\s*\n\s*(.+?)(?:\n|$)',
        'ban_name_pattern': r'Application\s+(.+?)\s+BANNED',
        'redirect_name_pattern': r'redirected to\s+(.+?)\s+([a-zA-Z0-9\.]+)\s*\(https',
        'bundle_pattern': None,
        'url_in_ban': True,
        'extract_bundle_from_url': True,
        'geo_pattern': r'🌏 The app is available in all geos except the following:\s*(.+?)(?:\n|$)',
        'sources_pattern': r'➡️ Available sources:\s*(.+?)(?:\n|$)',
        'onelink_pattern': r'❗️.*OneLink.*❗️',
        'macro_pattern': r'❗️.*automatic collection of macros.*❗️'
    },
    
    'td_appsbot': {
        'new_app_patterns': [r'Добавлено новое приложение', r'🟢 FREE 🟢'],
        'ban_patterns': [r'‼️ BAN ‼️'],
        'skip_patterns': [],
        'name_pattern': r'Название приложения:\s*(.+?)(?:\n|$)',
        'bundle_pattern': r'Имя пакета:\s*([^\s\n]+)',
        'url_pattern': r'https://play\.google\.com/store/apps/details\?id=([^\s&]+)',
        'ban_name_pattern': r'TDApps \| (.+?)(?:\n|$)'
    },
    
    'trident_appbot': {
        'new_app_patterns': [
            r'🔥Добавлено новое приложение',
            r'🔥 Добавлено новое приложение'
        ],
        'ban_patterns': [
            r'⛔️ Приложение:.*в бане',
            r'⛔️ Приложение:.*вв бане',
            r'в бане'
        ],
        'skip_patterns': [
            r'🟢.*доступно к заливу',
            r'поймало метку Facebook',
            r'остановите ФБ трафик'
        ],
        'name_pattern': r'🔥Добавлено новое приложение\s+\[(.+?)\]',
        'ban_name_pattern': r'⛔️ Приложение:\s*\[(.+?)\]',
        'url_pattern': r'https://play\.google\.com/store/apps/details\?id=([^\s&)]+)',
        'extract_bundle_from_url': True
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
DAYS_TO_LOAD = 60  # За сколько дней загружать историю (увеличено для захвата приложений которые могли быть забанены позже)
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
SHEET_RANGE = f'{SHEET_NAME}!A2:N'  # Начиная со второй строки (первая - заголовки), расширено до N для новых полей

# URL таблицы для быстрого доступа
SPREADSHEET_URL = f'https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}'