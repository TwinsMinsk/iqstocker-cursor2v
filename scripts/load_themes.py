"""
Скрипт для загрузки тем из CSV файла в базу данных

Использование:
    poetry run python scripts/load_themes.py
"""

import asyncio
import csv
import io
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.config.settings import settings
from src.database.connection import AsyncSessionLocal, engine
from src.database.models import ThemeTemplate

logger = get_logger(__name__)


async def load_themes_from_csv(csv_path: str, category: str = "photos") -> int:
    """
    Загрузить темы из CSV файла в базу данных
    
    Args:
        csv_path: Путь к CSV файлу
        category: Категория тем (по умолчанию photos)
        
    Returns:
        Количество загруженных тем
    """
    loaded_count = 0
    
    async with AsyncSessionLocal() as session:
        try:
            # Читаем CSV файл
            with open(csv_path, 'r', encoding='utf-8-sig') as f:
                content = f.read()
            
            # Парсим CSV
            reader = csv.reader(io.StringIO(content))
            rows = list(reader)
            
            for row in rows:
                if not row or not row[0]:
                    continue
                
                theme_text = row[0].strip()
                
                if not theme_text:
                    continue
                
                # Проверяем, существует ли уже такая тема
                from sqlalchemy import select
                statement = select(ThemeTemplate).where(
                    ThemeTemplate.theme == theme_text,
                    ThemeTemplate.category == category,
                )
                result = await session.execute(statement)
                existing = result.scalar_one_or_none()
                
                if existing:
                    continue  # Пропускаем дубликаты
                
                # Создаем шаблон темы
                template = ThemeTemplate(
                    category=category,
                    theme=theme_text,
                    description=None,
                    keywords=None,
                    is_active=True,
                )
                
                session.add(template)
                loaded_count += 1
            
            await session.commit()
            
            logger.info(
                "themes_loaded",
                csv_path=csv_path,
                category=category,
                count=loaded_count,
            )
        
        except Exception as e:
            await session.rollback()
            logger.error("themes_load_error", error=str(e), exc_info=True)
            raise
    
    return loaded_count


async def main():
    """Главная функция"""
    # Путь к CSV файлу
    csv_path = Path("Стоки 2(ТЕМЫ ИТОГ).csv")
    
    if not csv_path.exists():
        logger.error("csv_file_not_found", path=str(csv_path))
        return
    
    # Распределяем темы по категориям
    # Для MVP все темы идут в категорию photos
    # В будущем можно улучшить распределение
    categories = {
        "photos": csv_path,
    }
    
    total_loaded = 0
    
    for category, path in categories.items():
        count = await load_themes_from_csv(str(path), category=category)
        total_loaded += count
        logger.info("category_loaded", category=category, count=count)
    
    logger.info("themes_load_complete", total=total_loaded)
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

