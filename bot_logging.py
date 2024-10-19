import logging
import asyncio


class TelegramLogHandler(logging.Handler):
    def __init__(self, logger_bot, log_chat_id):
        super().__init__()
        self.logger_bot = logger_bot
        self.log_chat_id = log_chat_id

    async def emit_async(self, record):
        async with self.logger_bot:
            await self.logger_bot.send_message(
                chat_id=self.log_chat_id,
                text=self.format(record)
            )

    def emit(self, record):
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            asyncio.create_task(self.emit_async(record))
        else:
            asyncio.run(self.emit_async(record))


def setup_logger(logger_bot, log_chat_id):
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    telegram_handler = TelegramLogHandler(logger_bot, log_chat_id)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    telegram_handler.setFormatter(formatter)
    logger.addHandler(telegram_handler)
