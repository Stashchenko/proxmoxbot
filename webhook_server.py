from aiohttp import web


class WebhookServer:
    def __init__(self, bot):
        self.bot = bot

    async def handle_webhook(self, request):
        data = await request.json()
        severity = data.get("severity", "info")
        title = data.get("title", "No title")
        message = data.get("message", "")
        emoji = {"error": "❌", "warning": "⚠️", "info": "ℹ️"}.get(severity, "ℹ️")
        text = f"{emoji} *{title}*\n{message}\nSeverity: {severity}"
        await self.bot.send_message(text)
        return web.Response(text="OK")

    async def start(self):
        app = web.Application()
        app.router.add_post('/proxmox-webhook', self.handle_webhook)
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, "0.0.0.0", 3001)
        await site.start()
        print("🌐 Webhook server running on port 3001")
