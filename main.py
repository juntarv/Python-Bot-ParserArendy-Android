#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RentBot - Система мониторинга конкурентных приложений
Главное меню для запуска различных функций
"""

import asyncio
import sys
import os
from datetime import datetime

def print_header():
    """Выводит заголовок программы"""
    print("=" * 60)
    print("🤖 RentBot - Мониторинг конкурентных приложений")
    print("=" * 60)
    print(f"📅 Время запуска: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}")
    print()

def print_menu():
    """Выводит главное меню"""
    print("📋 Доступные действия:")
    print()
    print("1️⃣  Загрузить историю сообщений в канал")
    print("2️⃣  Синхронизировать канал с Google Таблицей")
    print("3️⃣  Очистить канал")
    print("4️⃣  Быстрая очистка канала (без подтверждения)")
    print("5️⃣  Показать конфигурацию")
    print("0️⃣  Выход")
    print()

async def load_history():
    """Загружает историю сообщений"""
    print("🚀 Запуск загрузки истории...")
    from load_history_fixed import main as load_main
    await load_main()

async def sync_to_sheets():
    """Синхронизирует с Google Таблицей"""
    print("📊 Запуск синхронизации с Google Таблицей...")
    from channel_to_sheets import main as sheets_main
    await sheets_main()

async def clear_channel():
    """Очищает канал с подтверждением"""
    print("🧹 Запуск очистки канала...")
    from clean_channel import main as clean_main
    await clean_main()

async def quick_clear_channel():
    """Быстро очищает канал без подтверждения"""
    print("⚡ Быстрая очистка канала...")
    from clean_channel import quick_clear_channel as quick_clean
    await quick_clean()

def show_config():
    """Показывает текущую конфигурацию"""
    print("⚙️ Текущая конфигурация:")
    print("-" * 40)
    
    try:
        import config
        print(f"📱 Мой канал ID: {config.MY_CHANNEL_ID}")
        print(f"📅 Дней для загрузки: {config.DAYS_TO_LOAD}")
        print(f"⏱️ Задержка между сообщениями: {config.DELAY_BETWEEN_MESSAGES} сек")
        print(f"🔗 Google Таблица: {config.SPREADSHEET_ID}")
        print(f"📄 Диапазон: {config.SHEET_RANGE}")
        print()
        print("🤖 Настроенные боты:")
        for bot_name, bot_config in config.BOT_PARSERS.items():
            print(f"   • {bot_name}")
        print()
    except Exception as e:
        print(f"❌ Ошибка загрузки конфигурации: {e}")

async def main():
    """Главная функция"""
    print_header()
    
    while True:
        print_menu()
        
        try:
            choice = input("➤ Выберите действие (0-5): ").strip()
            print()
            
            if choice == "0":
                print("👋 До свидания!")
                break
            elif choice == "1":
                await load_history()
            elif choice == "2":
                await sync_to_sheets()
            elif choice == "3":
                await clear_channel()
            elif choice == "4":
                await quick_clear_channel()
            elif choice == "5":
                show_config()
            else:
                print("❌ Неверный выбор. Попробуйте еще раз.")
            
            print("\n" + "=" * 60)
            
        except KeyboardInterrupt:
            print("\n\n🛑 Операция прервана пользователем")
            break
        except Exception as e:
            print(f"❌ Произошла ошибка: {e}")
            print("Попробуйте еще раз или выберите другое действие.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Программа завершена")
        sys.exit(0) 