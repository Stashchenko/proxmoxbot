import json

from aiohttp import web


class WebhookServer:
    def __init__(self, bot):
        self.bot = bot

    async def handle_webhook(self, request):
        raw_body = await request.text()
        try:
            data = json.loads(raw_body)
        except json.JSONDecodeError:
            raw_body = raw_body.strip()
            raw_body = raw_body.replace('\n', '\\n').replace('\r', '\\r')
            # Replace single quotes with double quotes as a quick fix
            data = json.loads(raw_body)

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
