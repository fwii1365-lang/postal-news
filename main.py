
import feedparser
import os
from datetime import datetime, timedelta
from openai import OpenAI
import urllib.parse

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

DAYS_LIMIT = 14


# ===== 日付フィルタ =====
def is_recent(entry):
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        published = datetime(*entry.published_parsed[:6])
        return published >= datetime.now() - timedelta(days=DAYS_LIMIT)
    return False  # 日付なしは除外


# ===== ニュース取得 =====
def fetch_news():
    policy_news = []
    business_news = []
    seen = set()

    # ===== Google News =====
    policy_queries = [
        "postal regulation law",
        "postal policy reform government",
        "postal subsidy government",
        "universal service postal",
        "mail delivery regulation"
    ]

    business_queries = [
        "postal operator results",
        "logistics company strategy",
        "parcel delivery service change",
        "postal company profit",
        "delivery network expansion"
    ]

    def fetch_google(queries, target):
        for q in queries:
            url = "https://news.google.com/rss/search?q=" + urllib.parse.quote(q)
            feed = feedparser.parse(url)

            for e in feed.entries:
                if is_recent(e):
                    title = e.title.strip()
                    if title not in seen:
                        seen.add(title)
                        target.append({
                            "title": title,
                            "date": getattr(e, "published", ""),
                            "link": e.link
                        })

    fetch_google(policy_queries, policy_news)
    fetch_google(business_queries, business_news)

    # ===== 専門誌 =====
    specialist = [
        "https://postandparcel.info/feed/",
        "https://www.postaltimes.com/feed/",
        "https://www.supplychaindive.com/feeds/news/",
        "https://www.logisticsmgmt.com/rss/all",
        "https://www.joc.com/rss"
    ]

    for url in specialist:
        feed = feedparser.parse(url)
        for e in feed.entries:
            if is_recent(e):
                title = e.title.strip()
                if title not in seen:
                    seen.add(title)
                    entry = {
                        "title": title,
                        "date": getattr(e, "published", ""),
                        "link": e.link
                    }
                    # 両方に入れる（AIが判定）
                    policy_news.append(entry)
                    business_news.append(entry)

    return policy_news, business_news


# ===== AI分析 =====
def analyze(policy, business):
    today = datetime.now().strftime("%Y/%m/%d")

    def format_entries(entries):
        return "\n".join(
            [f"{e['title']} | {e['date']} | {e['link']}" for e in entries]
        )

    prompt = f"""
今日は{today}。

以下は世界中の郵政・物流関連情報である。

【政策候補】
{format_entries(policy)}

【事業者候補】
{format_entries(business)}

――――――――――――――

【処理】

① 政策・規制・制度変更を最低10件抽出
② 事業者の動きを最低10件抽出

③ 各ニュースについて以下を必ず整理

・When（日時）
・Who（主体）
・What（内容）
・Where（対象地域）
・Why（背景）
・How（手段）

④ 要約は以下とする

・原則 10〜15行程度
・制度・規制・財務など複雑なものは20〜30行程度まで許容
・短すぎて意味が分からない要約は禁止

⑤ 各記事について必ず以下を明示

・入手元（媒体名・機関）
・日付
・URL

⑥ 重複は統合

⑦ 不足する場合は関連性の高い情報で補完

――――――――――――――

■ 政策・規制・制度変更（政府・規制・国際機関）
■ 事業者の動き

――――――――――――――

【禁止】

・該当なし
・一般論
・推測
"""

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content


# ===== 実行 =====
if __name__ == "__main__":
    policy, business = fetch_news()
    report = analyze(policy, business)

    print(f"【郵政・物流ニュース {datetime.now().strftime('%Y/%m/%d')}】\n")
    print(report)
