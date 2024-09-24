import asyncio
import aiopath
import aioshutil
import argparse
import logging
from datetime import datetime

async def copy_file(source_path, dest_path):
    """
    Асинхронно копіює файл з source_path до dest_path.
    
    :param source_path: Шлях до вихідного файлу
    :param dest_path: Шлях, куди копіюється файл
    """
    try:
        # Створюємо батьківську директорію для файлу призначення, якщо вона не існує
        await aiopath.AsyncPath(dest_path).parent.mkdir(parents=True, exist_ok=True)
        # Асинхронно копіюємо файл
        await aioshutil.copy2(source_path, dest_path)
        # Логуємо успішне копіювання
        logging.info(f"Скопійовано: {source_path} -> {dest_path}")
    except Exception as e:
        # Логуємо помилку, якщо копіювання не вдалося
        logging.error(f"Помилка при копіюванні {source_path}: {str(e)}")

async def read_folder(source_folder, output_folder):
    """
    Рекурсивно читає всі файли та папки у source_folder та копіює їх у відповідні підпапки output_folder.
    
    :param source_folder: Шлях до вихідної папки
    :param output_folder: Шлях до папки призначення
    """
    source_path = aiopath.AsyncPath(source_folder)
    tasks = []

    # Асинхронно ітеруємося по вмісту папки
    async for entry in source_path.iterdir():
        if await entry.is_file():
            # Якщо це файл, визначаємо його розширення
            file_extension = entry.suffix.lower()
            if not file_extension:
                file_extension = 'no_extension'
            else:
                file_extension = file_extension[1:]  # Видаляємо крапку
            # Формуємо шлях призначення для файлу
            dest_path = aiopath.AsyncPath(output_folder) / file_extension / entry.name
            # Створюємо завдання для копіювання файлу
            tasks.append(asyncio.create_task(copy_file(str(entry), str(dest_path))))
        elif await entry.is_dir():
            # Якщо це папка, рекурсивно викликаємо read_folder для цієї папки
            tasks.append(asyncio.create_task(read_folder(str(entry), output_folder)))
    
    # Чекаємо завершення всіх завдань
    await asyncio.gather(*tasks)

async def main():
    """
    Головна асинхронна функція, яка парсить аргументи командного рядка, 
    налаштовує логування та запускає процес сортування.
    """
    # Налаштовуємо парсер аргументів командного рядка
    parser = argparse.ArgumentParser(description="Асинхронно сортує файли за розширеннями.")
    parser.add_argument("source_folder", help="Шлях до вихідної папки")
    parser.add_argument("output_folder", help="Шлях до папки призначення")
    args = parser.parse_args()

    # Перетворюємо вхідні аргументи на об'єкти AsyncPath
    source_folder = aiopath.AsyncPath(args.source_folder)
    output_folder = aiopath.AsyncPath(args.output_folder)

    # Налаштування логування
    log_filename = f"log_file_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),  # Логування у файл
            logging.StreamHandler()  # Логування в консоль
        ]
    )

    # Перевіряємо, чи існує вихідна папка
    if not await source_folder.is_dir():
        logging.error(f"Вихідна папка не існує: {source_folder}")
        return

    # Логуємо початок процесу сортування
    logging.info(f"Початок сортування. Вихідна папка: {source_folder}, Папка призначення: {output_folder}")
    
    # Запускаємо процес сортування
    await read_folder(source_folder, output_folder)
    
    # Логуємо завершення процесу сортування
    logging.info("Сортування завершено")

if __name__ == "__main__":
    # Запускаємо головну асинхронну функцію
    asyncio.run(main())
