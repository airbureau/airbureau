#!/usr/bin/env python3
import os
import asyncio
import logging
from telegram import TelegramBot, create_and_initialize_bot
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


class BotRunner:
    def __init__(self):
        self.token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.admin_chat_ids = [int(x) for x in os.getenv('ADMIN_CHAT_IDS', '').split(',') if x]
        self.bot = None

    async def setup(self):
        """Настройка бота"""
        if not self.token:
            raise ValueError("TELEGRAM_BOT_TOKEN not found in environment variables")

        if not self.admin_chat_ids:
            raise ValueError("ADMIN_CHAT_IDS not found in environment variables")

        self.bot = await create_and_initialize_bot(self.token, self.admin_chat_ids)

    async def send_startup_message(self):
        """Отправка сообщения о запуске"""
        startup_msg = """
🚀 <b>Бот успешно запущен!</b>

<b>Время запуска:</b> {time}

✅ Все системы работают нормально
        """.format(time=asyncio.get_event_loop().time())

        await self.bot.send_message_to_admins(startup_msg)

    def run(self):
        """Запуск бота"""
        try:
            # Запуск в режиме polling
            self.bot.run_polling()
        except KeyboardInterrupt:
            logging.info("Bot stopped by user")
        except Exception as e:
            logging.error(f"Bot error: {e}")


async def main():
    runner = BotRunner()
    await runner.setup()
    await runner.send_startup_message()
    runner.run()


if __name__ == '__main__':
    asyncio.run(main())