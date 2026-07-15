# 📦 Stock Tracker Bot

A Python-based stock monitoring application that automatically checks product availability and sends Telegram notifications when products come back in stock.

## ✨ Features

- 🔍 Automatic stock monitoring
- 🤖 Telegram Bot notifications
- 💬 Telegram Topics support
- 🛒 Flipkart support
- 📅 APScheduler for automatic checking
- 🌐 FastAPI REST APIs
- 🗄️ MySQL database
- 🎭 Playwright-based stock detection
- 📝 Logging support

## 🛠️ Tech Stack

- Python
- FastAPI
- MySQL
- SQLAlchemy
- Playwright
- APScheduler
- Telegram Bot API

## 📂 Project Structure

```
app/
├── database/
├── models/
├── routes/
├── scheduler/
├── schemas/
├── services/
├── trackers/
└── bot/
```

## 🚀 Installation

```bash
pip install -r requirements.txt
playwright install
```

## ▶️ Run

```bash
uvicorn main:app --reload
```

## 📌 Current Supported Stores

- Flipkart ✅

## 🚧 Planned Stores

- Amazon
- Croma
- Reliance Digital
- OnePlus Store