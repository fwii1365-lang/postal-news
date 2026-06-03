
import feedparser
import os
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
以下は世界のニュースである。

対象は、郵政事業および物流事業に関するものに限定する。

――――――――――――――

以下の情報を入手・整理すること：

■ 最新ニュース

■ 政策・規制・制度変更（最重要）
・各国の規制（新規制・改正検討や検討案公表、意見募集の動き、改正結果の実施の動き）
・規制緩和（サービス低下容認含む）
・規制の運用・モニタリング
・補助金等による事業者支援
・業界振興政策
・ユニバーサルサービス維持
・郵便局・ポスト維持政策（緩和容認含む）
・戸別配達からコミュニティメールボックスへの移行容認（緩和）
・公益的サービスの拡大

・UPUの制度・統計・調査・研究活動
・EU Directive、小包Directiveの改訂動向

■ 事業者の動き
・サービス変更
・利用者利便向上
・料金変更
・収益・利益最大化の動き
・コスト削減（サービスレベル低下含む）
・物流最適化
・AI活用
・他企業との提携、合併、事業譲渡、撤退
・多角化による収益源確保
・公的・公益的サービスの提供
・小包ロッカー等アクセスポイントの整備・維持
・郵便局または郵便配達員による現金アクセスサービス提供
・財務データ公表
・Annual Report（必ず確認）

――――――――――――――

【処理】

① 各ニュースを5行程度にまとめる
② 日本語で出力する
③ 必ずソースURLを記載する

④ 上記の区分に従って体系的に整理する

⑤ 無関係なニュースは除外する


※上記の項目は分類であり、すべて満たす必要はない。
いずれかに該当すれば対象とする。

※郵政・物流との関連性が一定程度認められる場合は対象に含める。

※該当するニュースが存在しない場合は、
「該当ニュースなし」とだけ簡潔に出力すること。

※調査方法や外部サイト（ロイター等）を参照するような助言は禁止する。

※URL先の内容を直接取得する必要はない。
提供されたタイトルおよび文脈から判断すること。


――――――――――――――

{text}
"""
    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

def create_report(news):
    today = datetime.now().strftime("%Y/%m/%d")
    report = f"【郵政・物流ニュース {today}】\n\n"

    for n in news:
        report += analyze(n) + "\n\n"

    return report

if __name__ == "__main__":
    news = fetch_news()
    report = create_report(news)

    print(report)
