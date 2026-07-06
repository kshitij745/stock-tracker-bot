# 📌 StockTracker – Real-time E-commerce Stock Monitoring System

## 📖 Description
StockTracker is an automated system that monitors product availability on Flipkart in real-time.  
It uses web scraping (Playwright), a scheduler (APScheduler), and Telegram Bot integration to send instant alerts when a product comes back in stock.

---

## ⚙️ Tech Stack
- Python
- Playwright
- APScheduler
- FastAPI (if used)
- SQLite / PostgreSQL
- Telegram Bot API

---

## 🚀 Features
- Real-time stock monitoring
- Automated scheduler (runs every 2 minutes)
- Playwright-based web scraping
- Telegram instant notifications
- Duplicate alert prevention using database

---

## 🧩 Architecture
Scheduler → Service Layer → Playwright Scraper → Database → Telegram Bot

---

## ▶️ How to Run
pip install -r requirements.txt  
python main.py

---

## 📌 API Endpoints
- GET /products  
- POST /products  
- GET /products/{id}/check-stock  

---

## ⚠️ Challenges Solved
- Flipkart blocking & timeout issues  
- Duplicate notification problem  
- Background scheduler management  