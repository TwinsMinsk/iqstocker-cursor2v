"""
Загрузка всех тем в Supabase через MCP

Автоматически загружает все темы из CSV пакетами
"""

import csv
import sys
from pathlib import Path

# Читаем все темы
CSV_FILE = Path("Стоки 2(ТЕМЫ ИТОГ).csv")
BATCH_SIZE = 100

def read_themes() -> list[str]:
    """Читает все темы из CSV"""
    themes = []
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if row and row[0]:
                theme = row[0].strip()
                if theme:
                    themes.append(theme)
    return themes

def generate_batch_sql(themes_batch: list[str]) -> str:
    """Генерирует SQL для пакета тем"""
    values = []
    for theme in themes_batch:
        # Экранируем одинарные кавычки
        theme_escaped = theme.replace("'", "''")
        values.append(f"('photos', '{theme_escaped}', true, NOW())")
    
    sql = f"""INSERT INTO theme_templates (category, theme, is_active, created_at)
VALUES {', '.join(values)}
ON CONFLICT DO NOTHING;"""
    return sql

if __name__ == "__main__":
    themes = read_themes()
    print(f"📊 Всего тем: {len(themes)}")
    print(f"📦 Пакетов по {BATCH_SIZE}: {(len(themes) + BATCH_SIZE - 1) // BATCH_SIZE}")
    
    # Генерируем SQL для всех пакетов
    batches = []
    for i in range(0, len(themes), BATCH_SIZE):
        batch = themes[i:i + BATCH_SIZE]
        sql = generate_batch_sql(batch)
        batches.append((i // BATCH_SIZE + 1, batch, sql))
    
    print(f"\n✅ SQL готов для {len(batches)} пакетов")
    print(f"\n💡 Используйте Supabase MCP для загрузки каждого пакета")

