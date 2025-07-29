#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
🤖 RentBot - Система мониторинга приложений конкурентов
Версия: 2.0
Автор: Уникальная обфусцированная реализация
"""

import asyncio
import sys
import json
from datetime import datetime
from config import *

class RentBotMain:
    """Главный класс для управления всеми функциями бота"""
    
    def __init__(self):
        self.start_time = datetime.now()
        print(f"""
{'='*60}
🤖 RENTBOT v2.0 - СИСТЕМА МОНИТОРИНГА КОНКУРЕНТОВ
{'='*60}
📅 Запуск: {self.start_time.strftime('%d.%m.%Y %H:%M:%S')}
🔧 Режим: Продакшн (обфусцировано)
📊 Мониторинг: {len(COMPETITOR_BOTS)} ботов
🎯 Канал: {MY_CHANNEL_ID}
{'='*60}
        """)
    
    def show_menu(self):
        """Показывает главное меню"""
        print("""
🎯 ВЫБЕРИТЕ ДЕЙСТВИЕ:

1️⃣  📡 Загрузить историю сообщений (новые)
2️⃣  🧹 Очистить канал полностью  
3️⃣  📊 Синхронизировать с Google Sheets
4️⃣  ⚙️  Показать конфигурацию
5️⃣  📈 Статистика работы
6️⃣  🔄 Мониторинг в реальном времени
7️⃣  🧪 Тестовый режим
0️⃣  ❌ Выход

        """)
    
    async def load_history(self):
        """Запускает загрузку истории"""
        print("\n🚀 Запуск загрузки истории...")
        try:
            from load_history_fixed import main as load_main
            await load_main()
        except ImportError as e:
            print(f"❌ Ошибка импорта: {e}")
        except Exception as e:
            print(f"❌ Ошибка выполнения: {e}")
    
    async def clear_channel(self):
        """Очищает канал"""
        print("\n🧹 Запуск очистки канала...")
        try:
            from clean_channel import clear_channel_no_confirm
            deleted = await clear_channel_no_confirm()
            print(f"✅ Удалено {deleted} сообщений")
        except ImportError as e:
            print(f"❌ Ошибка импорта: {e}")
        except Exception as e:
            print(f"❌ Ошибка выполнения: {e}")
    
    async def sync_sheets(self):
        """Синхронизирует с Google Sheets"""
        print("\n📊 Запуск синхронизации с Google Sheets...")
        try:
            from channel_to_sheets import main as sheets_main
            await sheets_main()
        except ImportError as e:
            print(f"❌ Ошибка импорта: {e}")
        except Exception as e:
            print(f"❌ Ошибка выполнения: {e}")
    
    def show_config(self):
        """Показывает текущую конфигурацию"""
        print(f"""
⚙️  КОНФИГУРАЦИЯ СИСТЕМЫ:
{'='*40}
📡 API ID: {API_ID}
📞 Телефон: {PHONE}
📊 Канал: {MY_CHANNEL_ID}

🤖 Отслеживаемые боты ({len(COMPETITOR_BOTS)}):
""")
        for i, bot in enumerate(COMPETITOR_BOTS, 1):
            print(f"   {i}. @{bot}")
        
        print(f"""
📋 Настройки:
   🔍 Фильтрация: {'Включена' if FILTER_BY_KEYWORDS else 'Выключена'}
   📅 История: {DAYS_TO_LOAD} дней
   ⏱️  Задержка: {DELAY_BETWEEN_MESSAGES} сек
   📊 Google Sheets: {SPREADSHEET_ID}
   
🔑 Ключевые слова: {len(ALL_KEYWORDS)} шт.
        """)
    
    def show_stats(self):
        """Показывает статистику"""
        uptime = datetime.now() - self.start_time
        print(f"""
📈 СТАТИСТИКА РАБОТЫ:
{'='*40}
⏱️  Время работы: {uptime}
🔧 Статус: Активен
📡 Последняя синхронизация: -
💾 Кэш: Очищен
        """)
    
    async def real_time_monitor(self):
        """Мониторинг в реальном времени"""
        print("""
🔄 МОНИТОРИНГ В РЕАЛЬНОМ ВРЕМЕНИ
⚠️  Функция в разработке
Используйте загрузку истории для получения новых сообщений
        """)
    
    async def test_mode(self):
        """Тестовый режим"""
        print("""
🧪 ТЕСТОВЫЙ РЕЖИМ
================
Тестируем подключение к Telegram API...
        """)
        try:
            from telethon import TelegramClient
            test_client = TelegramClient('test_session', API_ID, API_HASH)
            await test_client.start(PHONE)
            
            # Проверяем доступ к каналу
            channel = await test_client.get_entity(MY_CHANNEL_ID)
            print(f"✅ Канал доступен: {channel.title}")
            
            # Проверяем ботов
            for bot in COMPETITOR_BOTS[:2]:  # Проверяем первые 2 бота
                try:
                    bot_entity = await test_client.get_entity(bot)
                    print(f"✅ Бот доступен: @{bot} ({bot_entity.first_name})")
                except:
                    print(f"❌ Бот недоступен: @{bot}")
            
            await test_client.disconnect()
            print("✅ Тестирование завершено успешно")
            
        except Exception as e:
            print(f"❌ Ошибка тестирования: {e}")
    
    async def run(self):
        """Главный цикл программы"""
        while True:
            try:
                self.show_menu()
                choice = input("👉 Выберите действие (0-7): ").strip()
                
                if choice == '0':
                    print("\n👋 Выход из программы...")
                    break
                elif choice == '1':
                    await self.load_history()
                elif choice == '2':
                    await self.clear_channel()
                elif choice == '3':
                    await self.sync_sheets()
                elif choice == '4':
                    self.show_config()
                elif choice == '5':
                    self.show_stats()
                elif choice == '6':
                    await self.real_time_monitor()
                elif choice == '7':
                    await self.test_mode()
                else:
                    print("❌ Неверный выбор!")
                
                if choice != '0':
                    input("\n⏳ Нажмите Enter для продолжения...")
                    
            except KeyboardInterrupt:
                print("\n\n⚠️  Прервано пользователем")
                break
            except Exception as e:
                print(f"\n❌ Критическая ошибка: {e}")
                input("⏳ Нажмите Enter для продолжения...")

# Обфусцированный запуск
async def _0x4d41494e():
    """Обфусцированная точка входа"""
    _0x626f74 = RentBotMain()
    await _0x626f74.run()

if __name__ == '__main__':
    print("🚀 Инициализация RentBot...")
    try:
        asyncio.run(_0x4d41494e())
    except KeyboardInterrupt:
        print("\n👋 Программа завершена")
    except Exception as e:
        print(f"\n💥 Фатальная ошибка: {e}")
        sys.exit(1) 