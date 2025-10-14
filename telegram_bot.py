import asyncio

from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes


class TelegramBot:
    def __init__(self, token, allowed_ids, proxmox_service):
        self.token = token
        self.allowed_chat_ids = allowed_ids
        self.proxmox = proxmox_service
        self.app = ApplicationBuilder().token(self.token).build()

        self.app.add_handler(CommandHandler("vmlist", self.vmlist))
        self.app.add_handler(CommandHandler("startvm", lambda u, c: self.vm_action(u, c, "start")))
        self.app.add_handler(CommandHandler("stopvm", lambda u, c: self.vm_action(u, c, "stop")))
        self.app.add_handler(CommandHandler("restartvm", lambda u, c: self.vm_action(u, c, "restart")))
        self.app.add_handler(MessageHandler(filters.TEXT | filters.COMMAND, self.unknown))

    def _is_allowed(self, chat_id):
        return chat_id in self.allowed_chat_ids

    async def _startup_async(self, app):
        await app.bot.set_my_commands([
            ("vmlist", "Show all VMs and LXC containers"),
            ("startvm", "Start a VM or LXC container"),
            ("stopvm", "Stop a VM or LXC container"),
            ("restartvm", "Restart a VM or LXC container"),
        ])

    async def vmlist(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_chat.id): return
        items = self.proxmox.list_vms()
        msg = "💻 *VMs and LXC containers:*\n"
        for i in items:
            emoji = "✅" if i['status'] == 'running' else "❌"
            mem_percent = (i['mem_used'] / i['mem_max']) * 100
            msg += f"{i['type']}: {i['name']} ({i['vmid']}) — {emoji}\n"
            msg += f"CPU: {i['cpu']:.1f}% | RAM: {mem_percent:.1f}%\n\n"
        await update.message.reply_text(msg, parse_mode='Markdown')

    async def vm_action(self, update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
        if not self._is_allowed(update.effective_chat.id): return
        if not context.args:
            await update.message.reply_text(f"⚠️ Usage: /{action}vm <vmid>")
            return
        vmid = context.args[0]
        try:
            self.proxmox.control_vm(vmid, action)
            await update.message.reply_text(f"✅ VM {vmid} {action}ed successfully")
        except Exception as e:
            await update.message.reply_text(f"❌ Error: {e}")

    async def unknown(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self._is_allowed(update.effective_chat.id): return
        await update.message.reply_text("💬 Unknown command")

    async def send_message(self, msg):
        for chat_id in self.allowed_chat_ids:
            await self.app.bot.send_message(chat_id=chat_id, text=msg, parse_mode='Markdown')

    async def run(self):
        await self.app.initialize()
        await self._startup_async(self.app)
        await self.app.start()
        await self.app.updater.start_polling()  # async polli

    def start(self):
        asyncio.create_task(self.run())
        print("🤖 Telegram bot started successfully")
