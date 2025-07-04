import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import os
import threading
import asyncio
from datetime import datetime

# Импортируем наши модули
from config import *
from load_history_fixed import load_history
from channel_to_sheets import main as update_sheets

class TelegramMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Telegram Apps Monitor")
        self.root.geometry("800x600")
        
        # Загружаем конфигурацию
        self.load_config()
        
        # Создаем интерфейс
        self.create_widgets()
        
    def load_config(self):
        """Загружает конфигурацию из файла"""
        self.config_file = "app_config.json"
        
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "selected_bots": COMPETITOR_BOTS,
                "target_channel": MY_CHANNEL_ID,
                "google_sheet_id": SPREADSHEET_ID,
                "sheet_name": SHEET_NAME,
                "days_to_load": DAYS_TO_LOAD,
                "delay_between_messages": DELAY_BETWEEN_MESSAGES
            }
            self.save_config()
    
    def save_config(self):
        """Сохраняет конфигурацию в файл"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=2, ensure_ascii=False)
    
    def create_widgets(self):
        """Создает интерфейс приложения"""
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Вкладка настроек
        self.create_settings_tab(notebook)
        
        # Вкладка мониторинга
        self.create_monitor_tab(notebook)
        
        # Вкладка логов
        self.create_logs_tab(notebook)
        
    def create_settings_tab(self, notebook):
        """Вкладка с настройками"""
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Настройки")
        
        # Выбор ботов
        ttk.Label(settings_frame, text="Выберите ботов для мониторинга:").grid(row=0, column=0, columnspan=2, pady=10)
        
        # Фрейм для списка ботов
        bots_frame = ttk.Frame(settings_frame)
        bots_frame.grid(row=1, column=0, columnspan=2, padx=20, pady=5)
        
        self.bot_vars = {}
        for i, bot in enumerate(COMPETITOR_BOTS):
            var = tk.BooleanVar(value=bot in self.config["selected_bots"])
            self.bot_vars[bot] = var
            ttk.Checkbutton(bots_frame, text=f"@{bot}", variable=var).grid(row=i, column=0, sticky='w', padx=5, pady=2)
        
        # Настройки канала
        ttk.Label(settings_frame, text="ID целевого канала:").grid(row=2, column=0, sticky='w', padx=20, pady=10)
        self.channel_entry = ttk.Entry(settings_frame, width=30)
        self.channel_entry.insert(0, str(self.config["target_channel"]))
        self.channel_entry.grid(row=2, column=1, padx=20, pady=10)
        
        # Настройки Google Sheets
        ttk.Label(settings_frame, text="Google Sheet ID:").grid(row=3, column=0, sticky='w', padx=20, pady=5)
        self.sheet_id_entry = ttk.Entry(settings_frame, width=30)
        self.sheet_id_entry.insert(0, self.config["google_sheet_id"])
        self.sheet_id_entry.grid(row=3, column=1, padx=20, pady=5)
        
        ttk.Label(settings_frame, text="Название листа:").grid(row=4, column=0, sticky='w', padx=20, pady=5)
        self.sheet_name_entry = ttk.Entry(settings_frame, width=30)
        self.sheet_name_entry.insert(0, self.config["sheet_name"])
        self.sheet_name_entry.grid(row=4, column=1, padx=20, pady=5)
        
        # Дополнительные настройки
        ttk.Label(settings_frame, text="Загружать за дней:").grid(row=5, column=0, sticky='w', padx=20, pady=5)
        self.days_spinbox = ttk.Spinbox(settings_frame, from_=1, to=90, width=10)
        self.days_spinbox.set(self.config["days_to_load"])
        self.days_spinbox.grid(row=5, column=1, sticky='w', padx=20, pady=5)
        
        ttk.Label(settings_frame, text="Задержка между сообщениями (сек):").grid(row=6, column=0, sticky='w', padx=20, pady=5)
        self.delay_spinbox = ttk.Spinbox(settings_frame, from_=1, to=30, width=10)
        self.delay_spinbox.set(self.config["delay_between_messages"])
        self.delay_spinbox.grid(row=6, column=1, sticky='w', padx=20, pady=5)
        
        # Кнопка сохранения
        ttk.Button(settings_frame, text="Сохранить настройки", command=self.save_settings).grid(row=7, column=0, columnspan=2, pady=20)
        
    def create_monitor_tab(self, notebook):
        """Вкладка мониторинга"""
        monitor_frame = ttk.Frame(notebook)
        notebook.add(monitor_frame, text="Мониторинг")
        
        # Кнопки действий
        actions_frame = ttk.Frame(monitor_frame)
        actions_frame.pack(pady=20)
        
        ttk.Button(actions_frame, text="Загрузить историю", command=self.load_history_thread).pack(side='left', padx=10)
        ttk.Button(actions_frame, text="Обновить Google Sheets", command=self.update_sheets_thread).pack(side='left', padx=10)
        ttk.Button(actions_frame, text="Запустить полный цикл", command=self.full_cycle_thread).pack(side='left', padx=10)
        
        # Прогресс бар
        self.progress = ttk.Progressbar(monitor_frame, mode='indeterminate')
        self.progress.pack(fill='x', padx=20, pady=10)
        
        # Статус
        self.status_label = ttk.Label(monitor_frame, text="Готов к работе")
        self.status_label.pack(pady=10)
        
        # Статистика
        stats_frame = ttk.LabelFrame(monitor_frame, text="Статистика последнего запуска")
        stats_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        self.stats_text = scrolledtext.ScrolledText(stats_frame, height=15, width=60)
        self.stats_text.pack(fill='both', expand=True, padx=10, pady=10)
        
    def create_logs_tab(self, notebook):
        """Вкладка с логами"""
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Логи")
        
        # Текстовое поле для логов
        self.log_text = scrolledtext.ScrolledText(logs_frame, height=25, width=80)
        self.log_text.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Кнопка очистки логов
        ttk.Button(logs_frame, text="Очистить логи", command=self.clear_logs).pack(pady=5)
        
    def save_settings(self):
        """Сохраняет настройки"""
        # Собираем выбранных ботов
        selected_bots = [bot for bot, var in self.bot_vars.items() if var.get()]
        
        # Обновляем конфигурацию
        self.config["selected_bots"] = selected_bots
        self.config["target_channel"] = int(self.channel_entry.get())
        self.config["google_sheet_id"] = self.sheet_id_entry.get()
        self.config["sheet_name"] = self.sheet_name_entry.get()
        self.config["days_to_load"] = int(self.days_spinbox.get())
        self.config["delay_between_messages"] = int(self.delay_spinbox.get())
        
        # Сохраняем в файл
        self.save_config()
        
        # Обновляем глобальные переменные
        global COMPETITOR_BOTS, MY_CHANNEL_ID, SPREADSHEET_ID, SHEET_NAME, DAYS_TO_LOAD, DELAY_BETWEEN_MESSAGES
        COMPETITOR_BOTS = selected_bots
        MY_CHANNEL_ID = self.config["target_channel"]
        SPREADSHEET_ID = self.config["google_sheet_id"]
        SHEET_NAME = self.config["sheet_name"]
        DAYS_TO_LOAD = self.config["days_to_load"]
        DELAY_BETWEEN_MESSAGES = self.config["delay_between_messages"]
        
        messagebox.showinfo("Успех", "Настройки сохранены!")
        self.log("Настройки обновлены")
        
    def log(self, message):
        """Добавляет сообщение в лог"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        
        self.log_text.insert('end', log_message)
        self.log_text.see('end')
        self.root.update()
        
    def clear_logs(self):
        """Очищает логи"""
        self.log_text.delete('1.0', 'end')
        
    def update_status(self, status):
        """Обновляет статус"""
        self.status_label.config(text=status)
        self.root.update()
        
    def load_history_thread(self):
        """Запускает загрузку истории в отдельном потоке"""
        thread = threading.Thread(target=self.load_history_async)
        thread.start()
        
    def load_history_async(self):
        """Асинхронная загрузка истории"""
        self.progress.start()
        self.update_status("Загружаю историю...")
        self.log("Начинаю загрузку истории")
        
        try:
            # Запускаем асинхронную функцию
            asyncio.run(load_history())
            self.log("Загрузка истории завершена успешно")
            self.update_status("Загрузка завершена")
            
            # Обновляем статистику
            self.update_stats()
            
        except Exception as e:
            self.log(f"Ошибка при загрузке истории: {e}")
            self.update_status("Ошибка загрузки")
            messagebox.showerror("Ошибка", f"Ошибка при загрузке истории:\n{e}")
        
        finally:
            self.progress.stop()
            
    def update_sheets_thread(self):
        """Запускает обновление Google Sheets в отдельном потоке"""
        thread = threading.Thread(target=self.update_sheets_async)
        thread.start()
        
    def update_sheets_async(self):
        """Асинхронное обновление Google Sheets"""
        self.progress.start()
        self.update_status("Обновляю Google Sheets...")
        self.log("Начинаю обновление Google Sheets")
        
        try:
            # Запускаем асинхронную функцию
            asyncio.run(update_sheets())
            self.log("Google Sheets обновлен успешно")
            self.update_status("Обновление завершено")
            
        except Exception as e:
            self.log(f"Ошибка при обновлении Google Sheets: {e}")
            self.update_status("Ошибка обновления")
            messagebox.showerror("Ошибка", f"Ошибка при обновлении Google Sheets:\n{e}")
        
        finally:
            self.progress.stop()
            
    def full_cycle_thread(self):
        """Запускает полный цикл в отдельном потоке"""
        thread = threading.Thread(target=self.full_cycle_async)
        thread.start()
        
    def full_cycle_async(self):
        """Полный цикл: загрузка истории + обновление таблицы"""
        self.log("Запускаю полный цикл обработки")
        
        # Сначала загружаем историю
        self.load_history_async()
        
        # Затем обновляем таблицу
        self.update_sheets_async()
        
        self.log("Полный цикл завершен")
        self.update_status("Готов к работе")
        
    def update_stats(self):
        """Обновляет статистику"""
        # Здесь можно добавить чтение статистики из последнего запуска
        stats_text = """Последний запуск:
        
Всего проверено сообщений: XXX
Переслано в канал: XXX

По типам:
- Новые приложения: XXX
- Баны: XXX
- Обновления: XXX

По ботам:
- @wwapps_bot: XXX
- @banda_rent_apps_bot: XXX
- @td_appsbot: XXX
"""
        self.stats_text.delete('1.0', 'end')
        self.stats_text.insert('1.0', stats_text)

def main():
    root = tk.Tk()
    app = TelegramMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()