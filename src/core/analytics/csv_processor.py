"""
Процессор CSV файлов от Adobe Stock

Парсит CSV файлы и извлекает данные для анализа
"""

import csv
import io
from datetime import datetime
from typing import Any

from src.config.logging import get_logger
from src.core.exceptions import CSVValidationException

logger = get_logger(__name__)


class CSVProcessor:
    """Процессор CSV файлов"""
    
    @staticmethod
    def parse_csv(content: bytes | str) -> list[dict[str, Any]]:
        """
        Парсить CSV файл и извлечь данные
        
        Поддерживает два формата:
        1. С заголовками: Date,Asset ID,Title,Type,Impressions,Downloads,Revenue
        2. Без заголовков (формат Adobe Stock): Date,Asset ID,Title,Type,Revenue,Category,Filename,Studio,Size
        
        Args:
            content: Содержимое CSV файла (bytes или str)
            
        Returns:
            Список словарей с данными
            
        Raises:
            CSVValidationException: Ошибка парсинга CSV
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
                raise CSVValidationException("CSV файл пуст")
            
            # Пытаемся определить формат по первой строке
            first_row = rows[0]
            
            # Проверяем наличие заголовков
            has_header = any(
                header.lower() in ['date', 'asset id', 'title', 'type', 'revenue']
                for header in first_row
            )
            
            if has_header:
                # Формат с заголовками
                return CSVProcessor._parse_with_headers(rows)
            else:
                # Формат Adobe Stock без заголовков
                return CSVProcessor._parse_adobe_stock_format(rows)
        
        except csv.Error as e:
            logger.error("csv_parse_error", error=str(e), exc_info=True)
            raise CSVValidationException(f"Ошибка парсинга CSV: {str(e)}")
        except Exception as e:
            logger.error("csv_processing_error", error=str(e), exc_info=True)
            raise CSVValidationException(f"Ошибка обработки CSV: {str(e)}")
    
    @staticmethod
    def _parse_with_headers(rows: list[list[str]]) -> list[dict[str, Any]]:
        """
        Парсить CSV с заголовками
        
        Args:
            rows: Список строк CSV
            
        Returns:
            Список словарей с данными
        """
        headers = [h.strip().lower() for h in rows[0]]
        data_rows = rows[1:]
        
        result = []
        for row in data_rows:
            if not row or len(row) < len(headers):
                continue
            
            row_dict = {}
            for i, header in enumerate(headers):
                if i < len(row):
                    row_dict[header] = row[i].strip()
            
            # Нормализуем данные
            normalized = CSVProcessor._normalize_row(row_dict)
            if normalized:
                result.append(normalized)
        
        return result
    
    @staticmethod
    def _parse_adobe_stock_format(rows: list[list[str]]) -> list[dict[str, Any]]:
        """
        Парсить формат Adobe Stock без заголовков
        
        Формат: Date,Asset ID,Title,Type,Revenue,Category,Filename,Studio,Size
        
        Args:
            rows: Список строк CSV
            
        Returns:
            Список словарей с данными
        """
        result = []
        
        for row in rows:
            if not row or len(row) < 5:
                continue
            
            try:
                # Парсим строку
                # Формат: Date,Asset ID,Title,Type,Revenue,Category,Filename,Studio,Size
                date_str = row[0].strip()
                asset_id = row[1].strip()
                title = row[2].strip()
                purchase_type = row[3].strip()  # subscription/custom
                revenue_str = row[4].strip().replace('$', '').replace(',', '')
                
                # Категория (если есть)
                category = row[5].strip() if len(row) > 5 else "unknown"
                
                # Парсим дату
                try:
                    date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except (ValueError, AttributeError):
                    # Пытаемся другие форматы
                    try:
                        date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                    except ValueError:
                        logger.warning("date_parse_warning", date_str=date_str)
                        date_obj = datetime.utcnow()
                
                # Парсим revenue
                try:
                    revenue = float(revenue_str)
                except (ValueError, TypeError):
                    revenue = 0.0
                
                # Считаем impressions и downloads
                # В этом формате нет этих данных, используем defaults
                impressions = 1  # По умолчанию
                downloads = 1 if revenue > 0 else 0
                
                row_dict = {
                    "date": date_obj.isoformat(),
                    "asset_id": asset_id,
                    "title": title,
                    "purchase_type": purchase_type,
                    "revenue": revenue,
                    "category": category,
                    "impressions": impressions,
                    "downloads": downloads,
                }
                
                result.append(row_dict)
            
            except Exception as e:
                logger.warning(
                    "row_parse_warning",
                    row=row,
                    error=str(e),
                )
                continue
        
        return result
    
    @staticmethod
    def _normalize_row(row_dict: dict[str, Any]) -> dict[str, Any] | None:
        """
        Нормализовать строку данных
        
        Args:
            row_dict: Словарь с данными строки
            
        Returns:
            Нормализованный словарь или None если невалидный
        """
        try:
            # Парсим дату
            date_str = str(row_dict.get("date", ""))
            try:
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except (ValueError, AttributeError):
                try:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    return None
            row_dict["date"] = date_obj.isoformat()
            
            # Парсим revenue
            revenue_str = str(row_dict.get("revenue", "0")).replace('$', '').replace(',', '')
            try:
                row_dict["revenue"] = float(revenue_str)
            except (ValueError, TypeError):
                row_dict["revenue"] = 0.0
            
            # Парсим impressions
            impressions_str = str(row_dict.get("impressions", "0")).replace(',', '')
            try:
                row_dict["impressions"] = int(impressions_str)
            except (ValueError, TypeError):
                row_dict["impressions"] = 0
            
            # Парсим downloads
            downloads_str = str(row_dict.get("downloads", "0")).replace(',', '')
            try:
                row_dict["downloads"] = int(downloads_str)
            except (ValueError, TypeError):
                # Если downloads нет, но есть revenue - значит была продажа
                row_dict["downloads"] = 1 if row_dict["revenue"] > 0 else 0
            
            return row_dict
        
        except Exception as e:
            logger.warning("row_normalize_warning", row=row_dict, error=str(e))
            return None
    
    @staticmethod
    def validate_csv(data: list[dict[str, Any]]) -> bool:
        """
        Валидировать распарсенные данные
        
        Args:
            data: Список словарей с данными
            
        Returns:
            True если данные валидны
            
        Raises:
            CSVValidationException: Данные невалидны
        """
        if not data:
            raise CSVValidationException("CSV файл не содержит данных")
        
        required_fields = ["date", "revenue"]
        for row in data[:10]:  # Проверяем первые 10 строк
            for field in required_fields:
                if field not in row:
                    raise CSVValidationException(
                        f"Отсутствует обязательное поле: {field}"
                    )
        
        return True

