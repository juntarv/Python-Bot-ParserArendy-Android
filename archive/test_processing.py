#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
from channel_to_sheets import get_all_apps_from_channel

async def test_processing():
    print('🔍 Тестируем обработку данных...')
    apps = await get_all_apps_from_channel()
    
    print(f'\n📊 Всего приложений найдено: {len(apps)}')
    
    # Ищем Plinko Tap
    plinko_tap_found = False
    for app in apps:
        if 'Plinko Tap' in app['app_name']:
            plinko_tap_found = True
            print(f'\n✅ НАЙДЕН Plinko Tap:')
            print(f'   Название: {app["app_name"]}')
            print(f'   Статус: {app["status"]}')
            print(f'   Дата выхода: {app["release_date"]}')
            print(f'   Дата бана: {app["ban_date"]}')
            break
    
    if not plinko_tap_found:
        print('\n❌ Plinko Tap НЕ НАЙДЕН в обработанных данных!')
        print('\nПоказываем первые 10 приложений:')
        for i, app in enumerate(apps[:10]):
            print(f'  {i+1}. {app["app_name"]} - {app["status"]}')

if __name__ == "__main__":
    asyncio.run(test_processing()) 