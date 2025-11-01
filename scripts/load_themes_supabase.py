"""
Загрузка тем в Supabase через MCP

Читает CSV и загружает темы в Supabase через Supabase MCP
"""

import csv
from pathlib import Path

CSV_FILE = Path("Стоки 2(ТЕМЫ ИТОГ).csv")
BATCH_SIZE = 100  # Размер пакета для вставки

def read_themes() -> list[str]:
    """Читает темы из CSV файла"""
    themes = []
    
    with open(CSV_FILE, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0]:
                continue
            theme_text = row[0].strip()
            if theme_text:
                themes.append(theme_text)
    
    return themes

def generate_sql_batch(themes: list[str], category: str = "photos") -> str:
    """Генерирует SQL для вставки пакета тем"""
    values = []
    
    for theme in themes:
        # Экранируем одинарные кавычки и специальные символы
        theme_escaped = theme.replace("'", "''").replace("\\", "\\\\")
        values.append(f"('{category}', '{theme_escaped}', true, NOW())")
    
    sql = f"""
INSERT INTO theme_templates (category, theme, is_active, created_at)
VALUES {', '.join(values)}
ON CONFLICT DO NOTHING;
"""
    return sql

if __name__ == "__main__":
    if not CSV_FILE.exists():
        print(f"❌ CSV файл не найден: {CSV_FILE}")
        exit(1)
    
    print(f"📖 Читаю темы из {CSV_FILE}...")
    themes = read_themes()
    print(f"✅ Найдено тем: {len(themes)}")
    
    print(f"\n📦 Создано пакетов: {(len(themes) + BATCH_SIZE - 1) // BATCH_SIZE}")
    print(f"\n💡 Для загрузки используйте:")
    print(f"   mcp_supabase_execute_sql(project_id='zpotpummnbfdlnzibyqb', query=sql)")

