# 🤖 AirBureau Trading Bot

*Последнее обновление: {{LAST_UPDATE}}*

## 📊 Статус проекта
![GitHub Last Commit](https://img.shields.io/github/last-commit/airbureau/airbureau_bbt)
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/airbureau/airbureau_bbt/deploy.yml)

## 🚀 Быстрый старт

```bash
# Клонирование и настройка
git clone https://github.com/airbureau/airbureau_bbt.git
cd airbureau_bbt
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# На сервере (автоматически через GitHub Actions)
cd ~/airbureau
source venv/bin/activate
python run.py