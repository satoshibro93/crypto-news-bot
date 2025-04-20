import asyncio
import feedparser
import os
from telegram import Bot
from telegram.error import TelegramError
from datetime import datetime

TOKEN = os.getenv("TOKEN")
CHANNEL_ID = os.getenv("CHANNEL_ID")
CHECK_INTERVAL = 300
KEYWORDS_FILE = "keywords.txt"
SENT_LINKS_FILE = "sent_links.txt"

# Загрузка ключевых слов
with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
    KEYWORDS = [w.strip().lower() for w in f.read().split(",")]

# Загрузка уже отправленных ссылок
if os.path.exists(SENT_LINKS_FILE):
    with open(SENT_LINKS_FILE, "r", encoding="utf-8") as f:
        sent_links = set(line.strip() for line in f.readlines())
else:
    sent_links = set()

bot = Bot(token=TOKEN)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def contains_keywords(entry):
    text = (entry.title + " " + entry.get("summary", "")).lower()
    return any(k in text for k in KEYWORDS)

async def check_feeds():
    global sent_links
    feeds = [
        "https://ria.ru/export/rss2/politics/index.xml",
        "https://tass.ru/rss/v2.xml",
        "https://rssexport.rbc.ru/rbcnews/news/30/full.rss"
    ]
    for url in feeds:
        log(f"Проверка ленты: {url}")
        feed = feedparser.parse(url)
        for entry in feed.entries:
            if entry.link in sent_links:
                continue
            if contains_keywords(entry):
                msg = entry.title + "\n" + entry.link
                try:
                    await bot.send_message(chat_id=CHANNEL_ID, text=msg)
                    sent_links.add(entry.link)
                    with open(SENT_LINKS_FILE, "a", encoding="utf-8") as f:
                        f.write(entry.link + "\n")
                    log(f"✅ Отправлено: {entry.title}")
                except TelegramError as e:
                    log(f"Ошибка Telegram: {e}")
            else:
                log(f"Пропущено: {entry.title}")

async def main():
    log("Бот запущен.")
    while True:
        await check_feeds()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
