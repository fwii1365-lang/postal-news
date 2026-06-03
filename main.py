
import feedparser
import os
import requests
from datetime import datetime
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

RSS_FEEDS = [
    "https://www.upu.int/en/rss",
    "https://ec.europa.eu/commission/presscorner/api/rss"
]

def fetch_news():
    news = []
    for url in RSS_FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries[:5]:
            news.append(e.title + " " + e.link)
    return news

def analyze(text):
    prompt = f"""
以下のニュースを日本語で：

① 3行要約
② 分類（政策/DX/脱炭素/物流）
③ 日本への影響

{text}
"""
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role":"user","content":prompt}]
    )
    return res.choices[0].message.content

def create_report(news):
    today = datetime.now().strftime("%Y/%m/%d")
    report = f"【郵政・物流ニュース {today}】\\n\\n"

    for n in news:
        report += analyze(n) + "\\n\\n"

    return report

def send_teams(msg):
    webhook = os.getenv("TEAMS_WEBHOOK")
    if webhook:
        requests.post(webhook, json={"text": msg})

if __name__ == "__main__":
    news = fetch_news()
    report = create_report(news)

    send_teams(report)

    print(report)
