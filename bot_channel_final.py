import asyncio
import feedparser
from telegram import Bot
from telegram.error import TelegramError
import os
from datetime import datetime

# ===== НАСТРОЙКИ =====
TOKEN = "8109128132:AAEo0V-kK-6Do9EgzTm_DyrHanDQ8cvAmg8"
CHANNEL_ID = "@yufbotbho"
CHECK_INTERVAL = 300  # каждые 5 минут
SENT_LINKS_FILE = "sent_links.txt"
LOG_FILE = "log.txt"

# ===== ССЫЛКИ НА RSS =====
RSS_FEEDS = [
    "https://ria.ru/export/rss2/politics/index.xml",
    "https://tass.ru/rss/v2.xml",
    "https://rssexport.rbc.ru/rbcnews/news/30/full.rss",
    "https://www.gazeta.ru/export/rss/politics.xml",
    "https://rg.ru/xml/index.xml",
    "https://lenta.ru/rss/news",
    "https://aif.ru/rss/politics.php",
    "https://www.vedomosti.ru/rss/rubric/politics",
]

# ===== ЗАГРУЗКА КЛЮЧЕВЫХ СЛОВ =====
with open("keywords.txt", "r", encoding="utf-8") as f:
    KEYWORDS = [word.strip().lower() for word in f.read().split(",")]

# ===== ЗАГРУЗКА УЖЕ ОТПРАВЛЕННЫХ ССЫЛОК =====
if os.path.exists(SENT_LINKS_FILE):
    with open(SENT_LINKS_FILE, "r", encoding="utf-8") as f:
        sent_links = set(line.strip() for line in f.readlines())
else:
    sent_links = set()

# ===== TELEGRAM БОТ =====
bot = Bot(token=TOKEN)

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp} {message}\n")
    print(f"{timestamp} {message}")

def contains_keywords(entry):
    text = (entry.title + " " + entry.get("summary", "")).lower()
    return any(keyword in text for keyword in KEYWORDS)

async def check_feeds():
    global sent_links
    for url in RSS_FEEDS:
        log(f"Проверка ленты: {url}")
        feed = feedparser.parse(url)
        for entry in feed.entries:
            link = entry.link
            if link in sent_links:
                continue
            if contains_keywords(entry):
                try:
                    msg = entry.title + "\n" + link
                    await bot.send_message(chat_id=CHANNEL_ID, text=msg)
                    sent_links.add(link)
                    with open(SENT_LINKS_FILE, "a", encoding="utf-8") as f:
                        f.write(link + "\n")
                    log(f"Отправлено: {entry.title}")
                except TelegramError as e:
                    log(f"Ошибка при отправке: {e}")
            else:
                log(f"Пропущено (без ключевых слов): {entry.title}")

async def main():
    log("Бот запущен")
    # Тестовая отправка
    try:
        test_msg = "✅ Тест: бот работает, логирование включено.\nhttps://example.com/test"
        if test_msg not in sent_links:
            await bot.send_message(chat_id=CHANNEL_ID, text=test_msg)
            sent_links.add(test_msg)
            with open(SENT_LINKS_FILE, "a", encoding="utf-8") as f:
                f.write(test_msg + "\n")
            log("Тестовое сообщение отправлено")
    except TelegramError as e:
        log(f"Ошибка при отправке теста: {e}")

    while True:
        await check_feeds()
        await asyncio.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    asyncio.run(main())
