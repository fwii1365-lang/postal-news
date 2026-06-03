

from openai import OpenAI
import os
from datetime import datetime

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def analyze():
    today = datetime.now().strftime("%Y/%m/%d")

    prompt = f"""
今日は{today}。

世界中から郵政事業および物流事業に関する最新動向を収集し、整理せよ。

■対象
・各国政府、規制当局
・郵便事業者、物流企業
・UPU、EUなど国際機関
・NPO、公的機関
・その他関連主体

――――――――――――――

■情報源の優先順位

【レベル1・2（最優先・同順位）】
政府、規制当局、国際機関（UPU、EU等）、公的機関
＋
事業者公式情報（郵便・物流、Annual Report、プレスリリース）

【レベル3（専門情報：例示・非限定）】
業界専門メディア（例：Post&Parcel、Journal of Commerce、Logistics Management、Supply Chain Dive、Postal Timesなど）
※例示であり限定しない

【レベル4（一般メディア）】
世界中のニュース媒体（制限なし）

【レベル5（補完情報）】
ブログ、小規模媒体、専門家記事など

――――――――――――――

■収集ルール

・レベル1・2の情報を最優先として扱う
・ただしレベル3およびレベル4の情報も並行して収集する
・レベル5は補完情報として収集する

・上記いずれかの条件に該当すれば対象とする（完全一致不要）
・制度変更は検討段階も含める
・政策、規制、補助、ユニバーサルサービスを重視
・事業者の動き（料金、効率化、AI、提携等）も対象

――――――――――――――

■出力

① 最近の重要ニュースを最低10件抽出する

② 各ニュースについて：
・5行程度で要約
・分類（政策・規制・制度変更／事業者の動き）
・URLを必ず記載

③ レベル表示を必ず行う
（レベル3・レベル4・レベル5は必ず明示する）
※レベル1・2は明示不要

――――――――――――――

■禁止事項

・一般論
・調査方法の説明
・「該当なし」の出力
・URLが存在しない情報の作成

"""

    res = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )

    return res.choices[0].message.content

if __name__ == "__main__":
    report = analyze()
    print(report)
