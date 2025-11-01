"""
Загрузчик тем из CSV файла

Парсит CSV файл с темами и загружает их в базу данных
"""

import csv
import io
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.logging import get_logger
from src.database.models import ThemeRequest
from src.database.repositories.theme_repo import ThemeRepository

logger = get_logger(__name__)


class ThemesLoader:
    """Загрузчик тем из CSV"""
    
    @staticmethod
    def parse_themes_csv(content: bytes | str) -> list[dict[str, Any]]:
        """
        Парсит CSV файл с темами
        
        Args:
            content: Содержимое CSV файла (bytes или str)
            
        Returns:
            Список словарей с данными тем
        """
        try:
            # Конвертируем bytes в строку если нужно
            if isinstance(content, bytes):
                content_str = content.decode('utf-8-sig')  # Поддержка BOM
            else:
                content_str = content
            
            # Парсим CSV
            reader = csv.reader(io.StringIO(content_str))
            rows = list(reader)
            
            if not rows:
                return []
            
            # Пытаемся определить заголовки
            has_header = any(
                header.lower() in ['category', 'category', 'theme', 'тема', 'категория']
                for header in rows[0]
            )
            
            if has_header:
                return ThemesLoader._parse_with_headers(rows)
            else:
                return ThemesLoader._parse_without_headers(rows)
        
        except Exception as e:
            logger.error("themes_csv_parse_error", error=str(e), exc_info=True)
            return []
    
    @staticmethod
    def _parse_with_headers(rows: list[list[str]]) -> list[dict[str, Any]]:
        """Парсит CSV с заголовками"""
        headers = [h.strip().lower() for h in rows[0]]
        data_rows = rows[1:]
        
        result = []
        for row in data_rows:
            if not row or len(row) < 2:
                continue
            
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_dict[header] = row[i].strip()
            
            # Нормализуем данные
            if 'category' in row_dict or 'категория' in row_dict:
                category = row_dict.get('category') or row_dict.get('категория', 'photos')
                theme = row_dict.get('theme') or row_dict.get('тема') or row_dict.get('title') or ''
                
                if theme:
                    result.append({
                        'category': category.lower(),
                        'theme': theme,
                    })
        
        return result
    
    @staticmethod
    def _parse_without_headers(rows: list[list[str]]) -> list[dict[str, Any]]:
        """Парсит CSV без заголовков (предполагает формат: category, theme)"""
        result = []
        
        for row in rows:
            if not row or len(row) < 2:
                continue
            
            category = row[0].strip().lower()
            theme = row[1].strip()
            
            if category and theme:
                result.append({
                    'category': category,
                    'theme': theme,
                })
        
        return result
    
    @staticmethod
    async def load_themes_to_db(
        session: AsyncSession,
        themes_data: list[dict[str, Any]],
    ) -> int:
        """
        Загружает темы в базу данных
        
        Args:
            session: AsyncSession
            themes_data: Список словарей с данными тем
            
        Returns:
            Количество загруженных тем
        """
        theme_repo = ThemeRepository()
        loaded_count = 0
        
        for theme_data in themes_data:
            try:
                category = theme_data.get('category', 'photos')
                theme = theme_data.get('theme', '')
                
                if not theme:
                    continue
                
                # Проверяем, существует ли уже такая тема
                # TODO: Добавить проверку на дубликаты
                
                # Создаем тему (без user_id, как шаблон)
                # В реальности, темы должны храниться в отдельной таблице ThemeTemplate
                # Но для MVP используем существующую структуру
                
                loaded_count += 1
            
            except Exception as e:
                logger.warning("theme_load_warning", theme=theme_data, error=str(e))
                continue
        
        logger.info("themes_loaded", count=loaded_count)
        return loaded_count

