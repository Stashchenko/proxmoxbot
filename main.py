import asyncio
import os

from dotenv import load_dotenv

from proxmox_api import ProxmoxService
from proxmox_monitor import ProxmoxMonitor
from telegram_bot import TelegramBot
from webhook_server import WebhookServer

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ALLOWED_CHAT_IDS = [int(x) for x in os.getenv("ALLOWED_CHAT_IDS").split(",")]
PROXMOX_HOST = os.getenv("PROXMOX_HOST")
PROXMOX_USER = os.getenv("PROXMOX_USER")
PROXMOX_TOKEN_ID = os.getenv("PROXMOX_TOKEN_ID")
PROXMOX_SECRET = os.getenv("PROXMOX_SECRET")

# Initialize services
proxmox_service = ProxmoxService(PROXMOX_HOST, PROXMOX_USER, PROXMOX_TOKEN_ID, PROXMOX_SECRET)
telegram_bot = TelegramBot(BOT_TOKEN, ALLOWED_CHAT_IDS, proxmox_service)
webhook_server = WebhookServer(telegram_bot)
monitor = ProxmoxMonitor(telegram_bot, proxmox_service)


async def main():
    # Start webhook server as a background task
    await asyncio.create_task(webhook_server.start())
    # Start the Telegram bot
    telegram_bot.start()
    # Start memory monitoring
    monitor.start()

    # Keep running forever
    try:
        while True:
            await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print("🛑 Shutdown requested, exiting...")
        monitor.stop()
    finally:
        await telegram_bot.app.stop()  # cleanup on exit


if __name__ == "__main__":
    asyncio.run(main())
