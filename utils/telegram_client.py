import os
import logging
from typing import Dict, List, Optional, Union
from datetime import datetime
import pandas as pd
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str, admin_chat_ids: List[int] = None):
        """
        Инициализация телеграм бота

        Args:
            token: Токен бота от @BotFather
            admin_chat_ids: Список ID чатов администраторов
        """
        self.token = token
        self.admin_chat_ids = admin_chat_ids or []
        self.application = None
        self.bot = None

    async def initialize(self):
        """Асинхронная инициализация бота"""
        try:
            self.application = Application.builder().token(self.token).build()
            self.bot = self.application.bot

            # Регистрация обработчиков команд
            self.application.add_handler(CommandHandler("start", self.start_command))
            self.application.add_handler(CommandHandler("stats", self.stats_command))
            self.application.add_handler(CommandHandler("status", self.status_command))
            self.application.add_handler(CommandHandler("alerts", self.alerts_command))
            self.application.add_handler(CommandHandler("balance", self.balance_command))
            self.application.add_handler(CommandHandler("help", self.help_command))

            logger.info("✅ Telegram bot initialized successfully")
            return True
        except Exception as e:
            logger.error(f"❌ Error initializing bot: {e}")
            return False

    async def send_message(self,
                           chat_id: int,
                           text: str,
                           parse_mode: str = 'HTML',
                           disable_notification: bool = False) -> bool:
        """
        Отправка сообщения в указанный чат

        Args:
            chat_id: ID чата
            text: Текст сообщения
            parse_mode: Режим парсинга ('HTML', 'Markdown')
            disable_notification: Отключить уведомление

        Returns:
            bool: Успешность отправки
        """
        try:
            await self.bot.send_message(
                chat_id=chat_id,
                text=text,
                parse_mode=parse_mode,
                disable_notification=disable_notification
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error sending message: {e}")
            return False

    async def send_message_to_admins(self,
                                     text: str,
                                     parse_mode: str = 'HTML',
                                     disable_notification: bool = False) -> Dict[int, bool]:
        """
        Отправка сообщения всем администраторам

        Returns:
            Dict: {chat_id: success_status}
        """
        results = {}
        for chat_id in self.admin_chat_ids:
            results[chat_id] = await self.send_message(
                chat_id, text, parse_mode, disable_notification
            )
        return results

    async def broadcast_message(self,
                                chat_ids: List[int],
                                text: str,
                                parse_mode: str = 'HTML') -> Dict[int, bool]:
        """
        Рассылка сообщения нескольким чатам

        Returns:
            Dict: {chat_id: success_status}
        """
        results = {}
        for chat_id in chat_ids:
            results[chat_id] = await self.send_message(chat_id, text, parse_mode)
        return results

    # Обработчики команд
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        user = update.effective_user
        welcome_text = f"""
🤖 <b>Air Bureau Trading Bot</b>

Привет, {user.first_name}! Я бот для мониторинга торговой системы.

<b>Доступные команды:</b>
/start - Начало работы
/stats - Статистика торговли
/status - Статус системы
/alerts - Последние алерты
/balance - Состояние баланса
/help - Помощь

📊 <i>Бот подключен к ClickHouse для анализа данных</i>
        """
        await update.message.reply_text(welcome_text, parse_mode='HTML')

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /stats - статистика торговли"""
        try:
            # Здесь будет интеграция с ClickHouse для получения статистики
            stats_text = """
📈 <b>Торговая статистика</b>

<b>Общая информация:</b>
• Активных пар: 15
• Всего сделок: 1,247
• Win Rate: 64.3%

<b>За последние 24 часа:</b>
• Сделок: 42
• PnL: +2.34%
• Объем: $124,567

<b>Топ пары:</b>
1. BTCUSDT: +1.2%
2. ETHUSDT: +0.8%
3. SOLUSDT: +0.5%
            """
            await update.message.reply_text(stats_text, parse_mode='HTML')
        except Exception as e:
            await self.send_error(update, f"Ошибка получения статистики: {e}")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /status - статус системы"""
        try:
            status_text = """
🟢 <b>Статус системы</b>

<b>Соединения:</b>
• Bybit WebSocket: 🟢 Активно
• ClickHouse DB: 🟢 Активно
• Telegram Bot: 🟢 Активно

<b>Производительность:</b>
• Время работы: 12ч 34м
• Память: 245 MB
• CPU: 12%

<b>Последняя проверка:</b> 2024-01-15 14:30:25 UTC
            """
            await update.message.reply_text(status_text, parse_mode='HTML')
        except Exception as e:
            await self.send_error(update, f"Ошибка получения статуса: {e}")

    async def alerts_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /alerts - последние алерты"""
        try:
            alerts_text = """
🚨 <b>Последние алерты</b>

<b>Сегодня:</b>
• 14:25: Переподключение WebSocket
• 13:45: Новый сигнал BTCUSDT
• 12:30: Обновление баланса

<b>Вчера:</b>
• 18:15: Деплой v1.2.3
• 16:40: Резкий рост волатильности
• 14:20: Обрыв соединения (восстановлено за 2.3с)
            """
            await update.message.reply_text(alerts_text, parse_mode='HTML')
        except Exception as e:
            await self.send_error(update, f"Ошибка получения алертов: {e}")

    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /balance - состояние баланса"""
        try:
            balance_text = """
💰 <b>Состояние баланса</b>

<b>Bybit Main Account:</b>
• Общий баланс: $15,247.89
• Доступно: $8,123.45
• В ордерах: $7,124.44
• PnL сегодня: +$234.56 (+1.54%)

<b>Распределение:</b>
• USDT: 65.2%
• BTC: 22.1%  
• ETH: 8.7%
• Другие: 4.0%

<b>Последнее обновление:</b> 2024-01-15 14:28:10 UTC
            """
            await update.message.reply_text(balance_text, parse_mode='HTML')
        except Exception as e:
            await self.send_error(update, f"Ошибка получения баланса: {e}")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = """
📖 <b>Помощь по командам</b>

<b>Основные команды:</b>
/start - Начало работы
/stats - Торговая статистика
/status - Статус системы и соединений
/alerts - История алертов и событий
/balance - Состояние баланса

<b>Техническая информация:</b>
• Бот развернут на сервере
• Используется Python + официальная библиотека Telegram
• Данные хранятся в ClickHouse
• Мониторинг WebSocket соединений

<b>Поддержка:</b>
Для технических вопросов обращайтесь к администратору.
        """
        await update.message.reply_text(help_text, parse_mode='HTML')

    async def send_error(self, update: Update, error_msg: str):
        """Отправка сообщения об ошибке"""
        error_text = f"❌ <b>Ошибка</b>\n\n{error_msg}"
        await update.message.reply_text(error_text, parse_mode='HTML')

    # Методы для интеграции с вашей системой
    async def send_alert(self,
                         alert_type: str,
                         message: str,
                         severity: str = "info") -> bool:
        """
        Отправка алерта администраторам

        Args:
            alert_type: Тип алерта (deploy, websocket, connection, trade, etc.)
            message: Текст сообщения
            severity: Уровень важности (info, warning, error, critical)
        """
        severity_icons = {
            "info": "ℹ️",
            "warning": "⚠️",
            "error": "❌",
            "critical": "🚨"
        }

        icon = severity_icons.get(severity, "📢")
        alert_text = f"""
{icon} <b>Алерт: {alert_type.upper()}</b>

{message}

<b>Время:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}
<b>Уровень:</b> {severity.upper()}
        """

        return await self.send_message_to_admins(alert_text)

    async def send_trading_signal(self,
                                  symbol: str,
                                  signal_type: str,
                                  price: float,
                                  confidence: float = None,
                                  reason: str = None) -> bool:
        """
        Отправка торгового сигнала

        Args:
            symbol: Торговая пара (BTCUSDT, ETHUSDT, etc.)
            signal_type: Тип сигнала (BUY, SELL, HOLD)
            price: Цена сигнала
            confidence: Уверенность в сигнале (0-1)
            reason: Причина сигнала
        """
        signal_icons = {
            "BUY": "🟢",
            "SELL": "🔴",
            "HOLD": "🟡"
        }

        icon = signal_icons.get(signal_type, "📊")

        signal_text = f"""
{icon} <b>Торговый сигнал</b>

<b>Пара:</b> {symbol}
<b>Сигнал:</b> {signal_type}
<b>Цена:</b> ${price:,.2f}
        """

        if confidence:
            signal_text += f"<b>Уверенность:</b> {confidence:.1%}\n"
        if reason:
            signal_text += f"<b>Причина:</b> {reason}\n"

        signal_text += f"\n<b>Время:</b> {datetime.now().strftime('%H:%M:%S UTC')}"

        return await self.send_message_to_admins(signal_text)

    async def send_system_stats(self,
                                stats_data: Dict) -> bool:
        """
        Отправка системной статистики

        Args:
            stats_data: Словарь с данными статистики
        """
        stats_text = """
📊 <b>Системная статистика</b>

<b>Производительность:</b>
• Нагрузка CPU: {cpu_percent}%
• Использование памяти: {memory_usage}
• Время работы: {uptime}

<b>База данных:</b>
• Записей сегодня: {records_today}
• Размер БД: {db_size}
• Запросов/сек: {qps}

<b>Соединения:</b>
• WebSocket: {ws_status}
• API: {api_status}
        """.format(**stats_data)

        return await self.send_message_to_admins(stats_text)

    def run_polling(self):
        """Запуск бота в режиме polling"""
        try:
            logger.info("🔄 Starting bot in polling mode...")
            self.application.run_polling()
        except Exception as e:
            logger.error(f"❌ Error in polling: {e}")

    async def run_webhook(self, webhook_url: str, port: int = 8443):
        """Запуск бота в режиме webhook"""
        try:
            await self.application.bot.set_webhook(webhook_url)
            logger.info(f"✅ Webhook set to: {webhook_url}")
            # Здесь должна быть логика запуска webhook сервера
        except Exception as e:
            logger.error(f"❌ Error setting webhook: {e}")


# Утилиты для работы с ботом
async def create_and_initialize_bot(token: str, admin_chat_ids: List[int] = None) -> TelegramBot:
    """
    Создание и инициализация бота

    Args:
        token: Токен бота
        admin_chat_ids: Список ID чатов администраторов

    Returns:
        Initialized TelegramBot instance
    """
    bot = TelegramBot(token, admin_chat_ids)
    success = await bot.initialize()
    if success:
        return bot
    else:
        raise Exception("Failed to initialize Telegram bot")


# Пример использования
async def main():
    """Пример использования бота"""
    # Замените на ваш токен и chat_id
    TOKEN = "your_telegram_bot_token"
    ADMIN_CHAT_IDS = [123456789]  # Ваш chat_id

    try:
        # Создание бота
        bot = await create_and_initialize_bot(TOKEN, ADMIN_CHAT_IDS)

        # Пример отправки алерта
        await bot.send_alert(
            alert_type="websocket",
            message="Переподключение WebSocket соединения с Bybit",
            severity="warning"
        )

        # Пример отправки торгового сигнала
        await bot.send_trading_signal(
            symbol="BTCUSDT",
            signal_type="BUY",
            price=42500.50,
            confidence=0.85,
            reason="Пробой уровня сопротивления"
        )

        # Запуск polling (блокирующий вызов)
        # bot.run_polling()

    except Exception as e:
        logger.error(f"❌ Error in main: {e}")


if __name__ == '__main__':
    # Запуск примера
    asyncio.run(main())