"""
Unit тесты для CSVProcessor

Тестирование парсинга CSV файлов
"""

import pytest

from src.core.analytics.csv_processor import CSVProcessor
from src.core.exceptions import CSVValidationException


def test_parse_csv_with_headers():
    """Тест парсинга CSV с заголовками"""
    content = """Date,Asset ID,Title,Type,Impressions,Downloads,Revenue
2024-01-01,123456789,Example Image,Photo,1234,5,2.50
2024-01-02,987654321,Another Image,Photo,2000,10,5.00"""
    
    data = CSVProcessor.parse_csv(content)
    
    assert len(data) == 2
    assert data[0]["asset_id"] == "123456789"
    assert float(data[0]["revenue"]) == 2.50


def test_parse_csv_adobe_stock_format():
    """Тест парсинга CSV формата Adobe Stock"""
    content = """2024-01-01T10:00:00+00:00,123456789,Example Image,custom,$2.50,photos,image.jpg,Studio,XXL
2024-01-02T11:00:00+00:00,987654321,Another Image,subscription,$1.00,photos,image2.jpg,Studio,XXL"""
    
    data = CSVProcessor.parse_csv(content)
    
    assert len(data) >= 2
    assert "asset_id" in data[0]
    assert float(data[0]["revenue"]) == 2.50


def test_parse_csv_empty():
    """Тест парсинга пустого CSV"""
    content = ""
    
    with pytest.raises(CSVValidationException):
        CSVProcessor.parse_csv(content)

