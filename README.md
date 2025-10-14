# Proxmox Telegram Bot

This bot allows you to monitor and control your Proxmox VE infrastructure directly from Telegram.
You can list, start, stop, and restart VMs/LXC containers and receive webhook events + memory usage alerts.

<img src="https://github.com/user-attachments/assets/94852731-a441-44ac-821e-66aa829bdcdb" width="300">

## 📦 Features
  - 📋 List all VMs and LXC containers with CPU and memory usage
  - ▶️ Start / 🛑 Stop / 🔁 Restart VMs and LXCs
  - 📡 Receive webhook events from Proxmox
  - 🚨 Memory usage alerting (configurable threshold)
  - 🛡️ Access restricted to allowed chat IDs

### 🧰 Requirements
  - Python ≥ 3.9
  - Proxmox VE API token with required permissions
  - A Telegram Bot token (create via Telegram BotFather)

## ⚙️ Setup Instructions

### 1. 📥 Clone the Repository
```bash
git clone https://github.com/Stashchenko/proxmoxbot.git
cd proxmoxbot
```
### 1.1 Install Dependencies
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. 🔑 Create a Proxmox API Token
 - Log in to your Proxmox web UI.
 - Go to Datacenter → Permissions → API Tokens.
 - Create a token for a user with PVEVMAdmin or appropriate privileges.
 - Copy Token ID and Secret.

### 3. 📝 Create a .env File
Create a file named .env in the project root:
```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN
ALLOWED_CHAT_IDS=123456789,987654321
PROXMOX_HOST=192.168.1.11 # replace to your IP if the PVE host
PROXMOX_USER=botuser@pve # your proxmox bot user
PROXMOX_TOKEN_ID=bot-token
PROXMOX_SECRET=your_secret_here
```
> 💡 ALLOWED_CHAT_IDS should contain the Telegram chat IDs of users allowed to use the bot.

To get your chat ID, send a message to the bot and use:
```bash
https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates
```
### 4. 🚀 Run the Bot
```bash
python3 main.py
```
You should see:
```bash
🌐 Webhook server running on port 3001
🤖 Commands initialized successfully
🤖 Telegram bot started successfully
🖥️ Proxmox memory monitor started
```

### 🔗 Webhook Integration (Optional)

If you want to receive Proxmox events. On your Proxmox host, configure a webhook pointing to your bot server:
```bash
http://<bot_server_ip>:3001/proxmox-webhook
```
Body:
```json
{"title":"{{title}}","message":"{{message}}","severity":"{{severity}}"}
```
<img src="https://github.com/user-attachments/assets/ca0971f2-c1e1-4fbb-b5d5-9584a0818cdf" width="300">

Test sending a sample webhook — you should see the message in your Telegram chat.

<img src="https://github.com/user-attachments/assets/dd16d224-17c7-4f84-b149-a506a569d05b" width="300">



#### Run as a service (optional)
##### 1. Create the Systemd Service
```bash
sudo nano /etc/systemd/system/proxmox-bot.service
```
##### 2. Paste the following contents:
```
[Unit]
Description=Proxmox Telegram Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
ExecStartPre=/bin/sleep 30
ExecStart=/usr/bin/python3 /root/main.py
WorkingDirectory=/root
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```
##### 3. Enable and Start the Service

Reload systemd to recognize the new service:
```bash
sudo systemctl daemon-reload
```
Enable the service to start on boot:
```bash
sudo systemctl enable proxmox-bot
```
Start the service immediately:
```bash
sudo systemctl start proxmox-bot
```
Check the service status:
```bash
sudo systemctl status proxmox-bot
```
Chech logs:
```bash
journalctl -u proxmox-bot -f
```
