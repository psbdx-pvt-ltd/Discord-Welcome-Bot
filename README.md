# 🍥 Discord Welcome Bot (Naruto Style)

![Version](https://img.shields.io/badge/Version-1.0.1-blue?style=flat-square)
![Developer](https://img.shields.io/badge/Developer-PSBDx-orange?style=flat-square)
![License](https://img.shields.io/badge/License-PSBDx_Custom_Open_Source-red?style=flat-square)

> A high-performance Discord bot that generates custom "Ninja Style" welcome images using `Pillow`. It features a unique **"Discord-as-Database"** architecture, allowing it to run statelessly on free hosting platforms like Render without losing data.

---

### 📚 Documentation

Need more details? Click the button below to view the full documentation.

[![Read Documentation](https://img.shields.io/badge/📖_Read_Full_Documentation-Click_Here-2ea44f?style=for-the-badge&logo=gitbook)](https://documentations.psbdx.rf.gd/discord-welcome-bot/v1-0-1)

---

## ✨ Features

* **🎨 Dynamic Image Generation:** Creates a custom welcome card for every new user.
* **⚡ Naruto-Style Text:** Uses advanced image manipulation to render text in a "Half-Blue / Half-Yellow" gradient style.
* **📜 Scroll Memory (Stateless Storage):** Saves configuration (welcome messages) to a specific Discord channel as a `.json` attachment. Perfect for hosting services with ephemeral file systems (like Render Free Tier).
* **🖼️ Auto-Caching:** Fetches and caches background images from a source channel to ensure speed.
* **🤖 Slash Commands:** Includes modern Discord `/` commands.
* **🟢 24/7 Keep-Alive:** Built-in `aiohttp` web server to prevent the bot from sleeping when used with a Cron Job.

## 🛠️ Installation & Setup

### 1. Prerequisites
* Python 3.9+
* A Discord Bot Token
* The `njnaruto.ttf` font file (placed in the root directory).

### 2. Local Setup
```bash
# Clone the repository
git clone [https://github.com/PSBDx/discord-welcome-bot.git](https://github.com/PSBDx/discord-welcome-bot.git)

# Install dependencies
pip install -r requirements.txt

# Run the bot
python bot.py
