from proxmoxer import ProxmoxAPI


class ProxmoxService:
    def __init__(self, host, user, token_id, secret, verify_ssl=False):
        self.client = ProxmoxAPI(
            host,
            user=user,
            token_name=token_id,
            token_value=secret,
            verify_ssl=verify_ssl
        )

    def list_vms(self):
        items = []
        for node in self.client.nodes.get():
            node_name = node['node']

            for vm in self.client.nodes(node_name).qemu.get():
                status = self.client.nodes(node_name).qemu(vm['vmid']).status.current.get()
                items.append(self._build_vm_info("VM", vm, status))

            for ct in self.client.nodes(node_name).lxc.get():
                status = self.client.nodes(node_name).lxc(ct['vmid']).status.current.get()
                items.append(self._build_vm_info("LXC", ct, status))

        return sorted(items, key=lambda x: x['vmid'])

    def control_vm(self, vmid, action):
        node_name, vm_type = self._find_vm(vmid)
        if not node_name:
            raise ValueError(f"VM {vmid} not found")
        vm = getattr(self.client.nodes(node_name), vm_type)(vmid)
        if action == "start":
            vm.status.start.post()
        elif action == "stop":
            vm.status.stop.post()
        elif action == "restart":
            vm.status.stop.post()
            import time
            time.sleep(2)
            vm.status.start.post()
        else:
            raise ValueError(f"Unknown action {action}")

    def _find_vm(self, vmid):
        for node in self.client.nodes.get():
            node_name = node['node']
            for vm in self.client.nodes(node_name).qemu.get():
                if str(vm['vmid']) == str(vmid):
                    return node_name, "qemu"
            for ct in self.client.nodes(node_name).lxc.get():
                if str(ct['vmid']) == str(vmid):
                    return node_name, "lxc"
        return None, None

    def _build_vm_info(self, vm_type, data, status):
        return {
            "type": vm_type,
            "name": data['name'],
            "vmid": data['vmid'],
            "status": data['status'],
            "cpu": status.get('cpu', 0) * 100,
            "mem_used": status.get('mem', 0),
            "mem_max": status.get('maxmem', 1)
        }
