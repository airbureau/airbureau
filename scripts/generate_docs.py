### 2. СОЗДАЙТЕ СКРИПТ ДЛЯ АВТОМАТИЧЕСКОГО ОБНОВЛЕНИЯ
# !/usr/bin/env python3
"""
Скрипт для автоматического обновления документации
"""

import os
import sys
import datetime
from pathlib import Path
import subprocess

# Добавляем корневую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def get_project_structure():
    """Генерирует структуру проекта в виде Markdown"""
    structure = []
    exclude_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv', '.idea'}
    exclude_files = {'.env', '.gitignore'}

    for root, dirs, files in os.walk('.'):
        # Исключаем ненужные директории
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        level = root.count(os.sep) - 1
        indent = '  ' * level

        if level >= 0:
            # Добавляем директорию
            dir_name = os.path.basename(root) if root != '.' else 'project-root'
            if dir_name and dir_name not in exclude_dirs:
                structure.append(f"{indent}📁 {dir_name}/")

            # Добавляем файлы
            subindent = '  ' * (level + 1)
            for file in files:
                if file not in exclude_files and not file.startswith('.'):
                    structure.append(f"{subindent}📄 {file}")

    return '\n'.join(structure)


def get_available_commands():
    """Извлекает доступные команды из run.py"""
    commands = [
        "| Команда | Описание |",
        "|---------|----------|",
        "| `python run.py` | Главное меню управления |",
        "| `python test_clickhouse.py` | Проверка подключения к БД |",
        "| `python scripts/create_tables.py` | Создание таблиц в ClickHouse |",
        "| `python scripts/test_trading_data.py` | Тестовые торговые данные |",
        "| `python scripts/analyze_data.py` | Анализ торговых данных |",
        "| `python scripts/generate_docs.py` | Обновление документации |"
    ]
    return '\n'.join(commands)


def get_clickhouse_tables():
    """Генерирует описание таблиц ClickHouse"""
    tables = [
        "| Таблица | Колонки | Описание |",
        "|---------|---------|-----------|",
        "| `trades` | timestamp, symbol, side, price, quantity, trade_id, strategy | Сделки |",
        "| `orders` | timestamp, symbol, order_type, side, price, quantity, status, order_id, strategy | Ордера |",
        "| `market_data` | timestamp, symbol, open, high, low, close, volume, timeframe | Рыночные данные |",
        "| `strategy_metrics` | timestamp, strategy, pnl, drawdown, sharpe_ratio, total_trades, winning_trades | Метрики стратегий |"
    ]
    return '\n'.join(tables)


def get_troubleshooting():
    """Генерирует раздел устранения неисправностей"""
    troubleshooting = [
        "### 🔧 Частые проблемы и решения",
        "",
        "**Проблема**: ClickHouse подключение не работает",
        "```bash",
        "# Решение:",
        "python test_clickhouse.py",
        "# Проверить .env файл",
        "cat .env | grep CLICKHOUSE",
        "```",
        "",
        "**Проблема**: GitHub Actions деплой",
        "- Проверить [Actions tab](https://github.com/airbureau/airbureau_bbt/actions)",
        "- Убедиться что SSH ключ на сервере добавлен в GitHub Secrets",
        "",
        "**Проблема**: ModuleNotFoundError",
        "```bash",
        "# Решение:",
        "source venv/bin/activate",
        "pip install -r requirements.txt",
        "```"
    ]
    return '\n'.join(troubleshooting)


def update_readme():
    """Обновляет README.md с актуальной информацией"""
    template_path = Path('README.md')

    if not template_path.exists():
        print("❌ README.md не найден. Создайте файл по шаблону выше.")
        return False

    # Читаем шаблон
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Заменяем плейсхолдеры
    replacements = {
        '{{LAST_UPDATE}}': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        '{{PROJECT_STRUCTURE}}': get_project_structure(),
        '{{AVAILABLE_COMMANDS}}': get_available_commands(),
        '{{CLICKHOUSE_TABLES}}': get_clickhouse_tables(),
        '{{TROUBLESHOOTING}}': get_troubleshooting()
    }

    for placeholder, value in replacements.items():
        content = content.replace(placeholder, value)

    # Записываем обновленный файл
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("✅ Документация обновлена!")
    return True


def main():
    print("📝 Генерация документации...")
    if update_readme():
        # Показываем diff
        result = subprocess.run(['git', 'diff', 'README.md'], capture_output=True, text=True)
        if result.stdout:
            print("\n📋 Изменения в документации:")
            print(result.stdout)

        # Предлагаем закоммитить изменения
        print("\n💡 Документация обновлена. Не забудьте закоммитить изменения:")
        print("git add README.md")
        print('git commit -m "docs: auto-update documentation"')
        print("git push origin main")
    else:
        print("❌ Не удалось обновить документацию")


if __name__ == "__main__":
    main()