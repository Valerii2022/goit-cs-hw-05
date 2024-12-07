import asyncio
import aiofiles
from pathlib import Path
import argparse
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

async def copy_file(file_path: Path, output_folder: Path):
    """Копіює файл до відповідної підпапки у вихідній папці на основі розширення."""
    try:
        ext = file_path.suffix[1:] 
        if not ext:
            ext = "unknown"
        target_folder = output_folder / ext
        target_folder.mkdir(parents=True, exist_ok=True)

        target_file = target_folder / file_path.name
        async with aiofiles.open(file_path, 'rb') as src, aiofiles.open(target_file, 'wb') as dst:
            while chunk := await src.read(1024 * 1024): 
                await dst.write(chunk)
        
        logging.info(f"Копіювання {file_path} -> {target_file}")
    except Exception as e:
        logging.error(f"Помилка при копіюванні {file_path}: {e}")

async def read_folder(source_folder: Path, output_folder: Path):
    """Рекурсивно читає всі файли у вихідній папці та копіює їх асинхронно."""
    tasks = []
    for item in source_folder.rglob('*'):  
        if item.is_file():
            tasks.append(copy_file(item, output_folder))
    
    await asyncio.gather(*tasks) 

def main():
    parser = argparse.ArgumentParser(description="Сортування файлів за розширенням")
    parser.add_argument("source_folder", type=str, help="Вихідна папка для читання файлів")
    parser.add_argument("output_folder", type=str, help="Цільова папка для запису файлів")
    args = parser.parse_args()

    source_folder = Path(args.source_folder)
    output_folder = Path(args.output_folder)

    if not source_folder.exists() or not source_folder.is_dir():
        logging.error(f"Вихідна папка {source_folder} не існує або не є директорією.")
        return
    if not output_folder.exists():
        output_folder.mkdir(parents=True, exist_ok=True)

    asyncio.run(read_folder(source_folder, output_folder))

if __name__ == "__main__":
    main()
