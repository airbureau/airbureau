import os
import logging
from datetime import datetime
from telegram import Bot
from telegram.ext import Application, CommandHandler, ContextTypes
import threading

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_chat_ids = [int(x) for x in os.getenv('ADMIN_CHAT_IDS', '').split(',') if x]
        self.application = None
        self.bot_thread = None

    def start(self):
        """Запуск бота в отдельном потоке"""
        if not self.token:
            logger.error("❌ TELEGRAM_BOT_TOKEN not found in environment")
            return

        if self.bot_thread and self.bot_thread.is_alive():
            return

        self.bot_thread = threading.Thread(target=self._run_bot, daemon=True)
        self.bot_thread.start()
        logger.info("✅ Telegram Bot started in background thread")

    def _run_bot(self):
        """Запуск бота в отдельном потоке"""
        try:
            self.application = Application.builder().token(self.token).build()

            # Регистрация команд
            self.application.add_handler(CommandHandler("start", self._start_cmd))
            self.application.add_handler(CommandHandler("stats", self._stats_cmd))
            self.application.add_handler(CommandHandler("status", self._status_cmd))
            self.application.add_handler(CommandHandler("balance", self._balance_cmd))
            self.application.add_handler(CommandHandler("help", self._help_cmd))

            # Запускаем polling
            logger.info("🔄 Starting bot polling...")
            self.application.run_polling()

        except Exception as e:
            logger.error(f"❌ Bot error: {e}")

    # Команды от пользователей
    def _start_cmd(self, update, context):
        update.message.reply_text("🤖 Торговый бот активен")

    def _stats_cmd(self, update, context):
        update.message.reply_text("📊 Статистика обновляется...")

    def _status_cmd(self, update, context):
        update.message.reply_text("🟢 Все системы работают")

    def _balance_cmd(self, update, context):
        update.message.reply_text("💰 Баланс обновляется...")

    def _help_cmd(self, update, context):
        help_text = """
🤖 Доступные команды:
/start - Проверка работы бота
/stats - Торговая статистика  
/status - Статус системы
/balance - Состояние баланса
/help - Эта справка
        """
        update.message.reply_text(help_text)

    # Синхронные методы для отправки сообщений
    def send_alert(self, alert_type: str, message: str):
        """Простая отправка алерта (полностью синхронная)"""
        try:
            if not self.token:
                logger.error("❌ Token not available for sending alert")
                return

            text = f"🚨 {alert_type.upper()}\n{message}\nВремя: {datetime.now().strftime('%H:%M:%S')}"

            # Создаем временного бота для отправки
            temp_bot = Bot(self.token)
            for chat_id in self.admin_chat_ids:
                try:
                    temp_bot.send_message(chat_id=chat_id, text=text)
                    logger.info(f"✅ Alert sent to {chat_id}")
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки сообщения: {e}")

        except Exception as e:
            logger.error(f"❌ Ошибка отправки алерта: {e}")

    def send_signal(self, symbol: str, action: str, price: float):
        """Простая отправка торгового сигнала"""
        try:
            if not self.token:
                logger.error("❌ Token not available for sending signal")
                return

            text = f"📈 {symbol} {action} по {price}\nВремя: {datetime.now().strftime('%H:%M:%S')}"

            temp_bot = Bot(self.token)
            for chat_id in self.admin_chat_ids:
                try:
                    temp_bot.send_message(chat_id=chat_id, text=text)
                    logger.info(f"✅ Signal sent to {chat_id}")
                except Exception as e:
                    logger.error(f"❌ Ошибка отправки сигнала: {e}")

        except Exception as e:
            logger.error(f"❌ Ошибка отправки сигнала: {e}")


# Глобальный экземпляр бота
bot = TelegramBot()