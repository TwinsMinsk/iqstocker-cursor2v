"""
Загрузка тем через Supabase MCP пакетами

Загружает темы из CSV файла небольшими пакетами через Supabase MCP
"""

import csv
from pathlib import Path

CSV_FILE = "Стоки 2(ТЕМЫ ИТОГ).csv"
BATCH_SIZE = 50  # Размер пакета для вставки

def read_csv_themes(csv_path: str) -> list[str]:
    """Читает темы из CSV файла"""
    themes = []
    
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        for row in reader:
            if not row or not row[0]:
                continue
            
            theme_text = row[0].strip()
            if theme_text:
                themes.append(theme_text)
    
    return themes

def generate_insert_sql(themes: list[str], category: str = "photos") -> str:
    """Генерирует SQL для вставки тем"""
    values = []
    
    for theme in themes:
        # Экранируем одинарные кавычки
        theme_escaped = theme.replace("'", "''")
        values.append(f"('{category}', '{theme_escaped}', true, NOW())")
    
    sql = f"""
INSERT INTO theme_templates (category, theme, is_active, created_at)
VALUES {', '.join(values)}
ON CONFLICT DO NOTHING;
"""
    return sql

if __name__ == "__main__":
    csv_path = Path(CSV_FILE)
    
    if not csv_path.exists():
        print(f"❌ CSV файл не найден: {CSV_FILE}")
        exit(1)
    
    print(f"📖 Читаю темы из {CSV_FILE}...")
    themes = read_csv_themes(str(csv_path))
    print(f"✅ Найдено тем: {len(themes)}")
    
    print(f"\n📝 SQL для загрузки {len(themes)} тем:")
    print("=" * 70)
    
    # Разбиваем на пакеты
    for i in range(0, len(themes), BATCH_SIZE):
        batch = themes[i:i + BATCH_SIZE]
        sql = generate_insert_sql(batch)
        
        print(f"\n-- Пакет {i // BATCH_SIZE + 1} ({len(batch)} тем):")
        print(sql[:500] + "..." if len(sql) > 500 else sql)
    
    print("\n" + "=" * 70)
    print(f"\n💡 Для загрузки используйте Supabase MCP:")
    print(f"   mcp_supabase_execute_sql() с каждым пакетом SQL")

