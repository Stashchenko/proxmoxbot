import asyncio


class ProxmoxMonitor:
    def __init__(self, bot, proxmox, ignored_vmid_list=None, alert_threshold=80, interval=300):
        self.bot = bot
        self.proxmox = proxmox
        self.alert_threshold = alert_threshold
        self.ignored_vmid_list = ignored_vmid_list or []
        self.interval = interval
        self._task = None
        self._running = False

    async def _check_memory(self):
        while self._running:
            try:
                vms = self.proxmox.list_vms()  # ← use existing method
                for vm in vms:
                    if vm.get("vmid") in self.ignored_vmid_list:
                        continue
                    mem_used = vm.get("mem_used", 0)
                    mem_max = max(vm.get("mem_max", 1), 1)
                    mem_percent = (mem_used / mem_max) * 100

                    if mem_percent >= self.alert_threshold:
                        msg = (
                            f"⚠️ {vm['type']} *{vm['name']}* "
                            f"({vm['vmid']}) is using {mem_percent:.1f}% RAM "
                            f"({mem_used / 1024 / 1024:.0f} MB / {mem_max / 1024 / 1024:.0f} MB)"
                        )
                        await self.bot.send_message(msg)

            except Exception as e:
                print("❌ Memory monitoring error:", e, flush=True)

            await asyncio.sleep(self.interval)

    def start(self):
        if not self._running:
            self._running = True
            self._task = asyncio.create_task(self._check_memory())
            print("🖥️ Proxmox memory monitor started")

    def stop(self):
        if self._running:
            self._running = False
            if self._task:
                self._task.cancel()
            print("🛑 Proxmox memory monitor stopped")
