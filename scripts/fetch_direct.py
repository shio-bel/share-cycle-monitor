"""重要なページを直接監視するスクリプト"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional

# 共通キーワード
COMMON_KEYWORDS = [
    "シェアサイクル", "電動キックボード", "特定小型原動機付自転車", "特定小型原付",
    "マイクロモビリティ", "公募", "募集", "事業者", "プロポーザル",
    "自転車シェアリング", "コミュニティサイクル", "サイクルポート",
]

# 直接監視するページのリスト
WATCH_PAGES = [
    # 東京都
    {
        "url": "https://www.kotsu.metro.tokyo.jp/other/kanren/",
        "prefecture": "東京",
        "organization": "東京都交通局",
        "keywords": COMMON_KEYWORDS,
    },
    # 千代田区
    {
        "url": "https://www.city.chiyoda.lg.jp/koho/kuse/nyusatsu/proposal/index.html",
        "prefecture": "東京",
        "organization": "千代田区",
        "keywords": COMMON_KEYWORDS,
    },
    # 中央区
    {
        "url": "https://www.city.chuo.lg.jp/kusei/keiyakunyusatsu/propo/index.html",
        "prefecture": "東京",
        "organization": "中央区",
        "keywords": COMMON_KEYWORDS,
    },
    # 港区
    {
        "url": "https://www.city.minato.tokyo.jp/keiyaku/kuse/nyusatsu/keyaku/proposal.html",
        "prefecture": "東京",
        "organization": "港区",
        "keywords": COMMON_KEYWORDS,
    },
    # 新宿区
    {
        "url": "https://www.city.shinjuku.lg.jp/jigyo/index02_pps.html",
        "prefecture": "東京",
        "organization": "新宿区",
        "keywords": COMMON_KEYWORDS,
    },
    # 文京区
    {
        "url": "https://www.city.bunkyo.lg.jp/b003/p007435.html",
        "prefecture": "東京",
        "organization": "文京区",
        "keywords": COMMON_KEYWORDS,
    },
    # 台東区
    {
        "url": "https://www.city.taito.lg.jp/jigyosha/keiyaku/proposal/index.html",
        "prefecture": "東京",
        "organization": "台東区",
        "keywords": COMMON_KEYWORDS,
    },
    # 墨田区
    {
        "url": "https://www.city.sumida.lg.jp/kurashi/jitensha/bicycle/share_cycle.html",
        "prefecture": "東京",
        "organization": "墨田区",
        "keywords": COMMON_KEYWORDS,
    },
    # 江東区
    {
        "url": "https://www.city.koto.lg.jp/053101/20190319puropo.html",
        "prefecture": "東京",
        "organization": "江東区",
        "keywords": COMMON_KEYWORDS,
    },
    # 品川区
    {
        "url": "https://www.city.shinagawa.tokyo.jp/PC/kuseizyoho/kuseizyoho-siryo/kuseizyoho-siryo-keiyaku/kuseizyoho-siryo-keiyaku-hacchu/index.html",
        "prefecture": "東京",
        "organization": "品川区",
        "keywords": COMMON_KEYWORDS,
    },
    # 目黒区
    {
        "url": "https://www.city.meguro.tokyo.jp/shigoto/nyuusatsu/joujou/index.html",
        "prefecture": "東京",
        "organization": "目黒区",
        "keywords": COMMON_KEYWORDS,
    },
    # 大田区
    {
        "url": "https://www.city.ota.tokyo.jp/jigyousha/boshuu_shitei/index.html",
        "prefecture": "東京",
        "organization": "大田区",
        "keywords": COMMON_KEYWORDS,
    },
    # 世田谷区
    {
        "url": "https://www.city.setagaya.lg.jp/mokuji/kusei/002/003/index.html",
        "prefecture": "東京",
        "organization": "世田谷区",
        "keywords": COMMON_KEYWORDS,
    },
    # 渋谷区
    {
        "url": "https://www.city.shibuya.tokyo.jp/jigyosha/proposal/proposal/",
        "prefecture": "東京",
        "organization": "渋谷区",
        "keywords": COMMON_KEYWORDS,
    },
    # 中野区
    {
        "url": "https://www.city.tokyo-nakano.lg.jp/jigyosha/nyusatsu/jigyousyasentei-bosyu/index.html",
        "prefecture": "東京",
        "organization": "中野区",
        "keywords": COMMON_KEYWORDS,
    },
    # 杉並区
    {
        "url": "https://www.city.suginami.tokyo.jp/nyuusatsuoshirase/proposal/index.html",
        "prefecture": "東京",
        "organization": "杉並区",
        "keywords": COMMON_KEYWORDS,
    },
    # 豊島区
    {
        "url": "https://www.city.toshima.lg.jp/kuse/nyusatsu/proposal/bosyuu/index.html",
        "prefecture": "東京",
        "organization": "豊島区",
        "keywords": COMMON_KEYWORDS,
    },
    # 北区
    {
        "url": "https://www.city.kita.lg.jp/city-information/contract/1011617/1011618/index.html",
        "prefecture": "東京",
        "organization": "北区",
        "keywords": COMMON_KEYWORDS,
    },
    # 荒川区
    {
        "url": "https://www.city.arakawa.tokyo.jp/jigyousha/nyusatsu/proposal/index.html",
        "prefecture": "東京",
        "organization": "荒川区",
        "keywords": COMMON_KEYWORDS,
    },
    # 板橋区
    {
        "url": "https://www.city.itabashi.tokyo.jp/bunka/proposal/boshu/index.html",
        "prefecture": "東京",
        "organization": "板橋区",
        "keywords": COMMON_KEYWORDS,
    },
    # 練馬区
    {
        "url": "https://www.city.nerima.tokyo.jp/jigyoshamuke/jigyosha/oshirase/index.html",
        "prefecture": "東京",
        "organization": "練馬区",
        "keywords": COMMON_KEYWORDS,
    },
    # 足立区
    {
        "url": "https://www.city.adachi.tokyo.jp/shigoto/nyusatsu/jigyosha/proposal/index.html",
        "prefecture": "東京",
        "organization": "足立区",
        "keywords": COMMON_KEYWORDS,
    },
    # 葛飾区
    {
        "url": "https://www.city.katsushika.lg.jp/business/1000011/1000067/1005056/index.html",
        "prefecture": "東京",
        "organization": "葛飾区",
        "keywords": COMMON_KEYWORDS,
    },
    # 江戸川区
    {
        "url": "https://www.city.edogawa.tokyo.jp/shigotosangyo/proposal/index.html",
        "prefecture": "東京",
        "organization": "江戸川区",
        "keywords": COMMON_KEYWORDS,
    },
    # ===== 東京都本体（都庁各局） =====
    # 東京都環境局（シェアサイクル政策所管）
    {
        "url": "https://www.kankyo.metro.tokyo.lg.jp/vehicle/management/bycicle_sharing/index.html",
        "prefecture": "東京",
        "organization": "東京都環境局",
        "keywords": COMMON_KEYWORDS,
    },
    # 東京都都市整備局（都有地活用公募）
    {
        "url": "https://www.toshiseibi.metro.tokyo.lg.jp/machizukuri/machi_project/toshi_saisei/arichi_katuyou",
        "prefecture": "東京",
        "organization": "東京都都市整備局",
        "keywords": COMMON_KEYWORDS,
    },
    # 東京都公募・募集一覧ポータル
    {
        "url": "https://www.metro.tokyo.lg.jp/purpose/opencall",
        "prefecture": "東京",
        "organization": "東京都",
        "keywords": COMMON_KEYWORDS,
    },
    # 東京ベイeSGプロジェクト（モビリティ実証実験）
    {
        "url": "https://www.tokyobayesg.metro.tokyo.lg.jp/priorityprojects/recruitment2024.html",
        "prefecture": "東京",
        "organization": "東京ベイeSGプロジェクト",
        "keywords": COMMON_KEYWORDS + ["実証実験", "モビリティ"],
    },
    # 東京都港湾局（臨海副都心公募）
    {
        "url": "https://www.kouwan.metro.tokyo.lg.jp/rinkai/youkou/index.html",
        "prefecture": "東京",
        "organization": "東京都港湾局",
        "keywords": COMMON_KEYWORDS,
    },
    # ===== 沖縄県 =====
    # 沖縄県（公募・入札発注情報）
    {
        "url": "https://www.pref.okinawa.jp/shigoto/nyusatsukeiyaku/1015342/index.html",
        "prefecture": "沖縄",
        "organization": "沖縄県",
        "keywords": COMMON_KEYWORDS,
    },
    # 那覇市（募集情報）
    {
        "url": "https://www.city.naha.okinawa.jp/category/bosyu/index.html",
        "prefecture": "沖縄",
        "organization": "那覇市",
        "keywords": COMMON_KEYWORDS,
    },
    # 那覇市（入札・企画提案公告）
    {
        "url": "https://www.city.naha.okinawa.jp/business/touroku/nyuusatukoukoku/index.html",
        "prefecture": "沖縄",
        "organization": "那覇市",
        "keywords": COMMON_KEYWORDS,
    },
    # 石垣市（契約管財課・公募型プロポーザル）
    {
        "url": "https://www.city.ishigaki.okinawa.jp/soshiki/keiyaku_kanzai/2/index.html",
        "prefecture": "沖縄",
        "organization": "石垣市",
        "keywords": COMMON_KEYWORDS,
    },
    # ===== 横浜万博協会 =====
    {
        "url": "https://www.expo2027yokohama.or.jp/news/",
        "prefecture": "神奈川",
        "organization": "横浜万博協会",
        "keywords": COMMON_KEYWORDS + ["万博", "モビリティ"],
    },
    # ===== 政令指定都市 =====
    # 横浜市
    {
        "url": "https://www.city.yokohama.lg.jp/business/nyusatsu/keiyaku/proposal/",
        "prefecture": "神奈川",
        "organization": "横浜市",
        "keywords": COMMON_KEYWORDS,
    },
    # 川崎市
    {
        "url": "https://www.city.kawasaki.jp/jigyou/category/77-1-0-0-0-0-0-0-0-0.html",
        "prefecture": "神奈川",
        "organization": "川崎市",
        "keywords": COMMON_KEYWORDS,
    },
    # さいたま市
    {
        "url": "https://www.city.saitama.lg.jp/jigyosha/nyusatsu/proposal/index.html",
        "prefecture": "埼玉",
        "organization": "さいたま市",
        "keywords": COMMON_KEYWORDS,
    },
    # 千葉市
    {
        "url": "https://www.city.chiba.jp/zaiseikyoku/zaisei/keiyaku/proposal.html",
        "prefecture": "千葉",
        "organization": "千葉市",
        "keywords": COMMON_KEYWORDS,
    },
    # ===== シェアサイクル事業者 =====
    # ドコモ・バイクシェア
    {
        "url": "https://www.d-bikeshare.com/news/",
        "prefecture": "",
        "organization": "ドコモ・バイクシェア",
        "keywords": COMMON_KEYWORDS + ["連携", "協定", "新規"],
    },
    # HELLO CYCLING
    {
        "url": "https://www.hellocycling.jp/news/",
        "prefecture": "",
        "organization": "HELLO CYCLING",
        "keywords": COMMON_KEYWORDS + ["連携", "協定", "新規"],
    },
    # Luup
    {
        "url": "https://luup.sc/news/",
        "prefecture": "",
        "organization": "Luup",
        "keywords": COMMON_KEYWORDS + ["連携", "協定", "新規"],
    },
]


def fetch_page(url: str) -> str:
    """ページを取得"""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; ShareCycleMonitor/1.0)"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"ページ取得エラー ({url}): {e}")
        return ""


def extract_update_date(soup: BeautifulSoup, text: str) -> Optional[str]:
    """ページから更新日を抽出"""
    # パターン1: 「更新日：2025年12月24日」形式
    patterns = [
        r'更新日[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)',
        r'最終更新[：:]\s*(\d{4}年\d{1,2}月\d{1,2}日)',
        r'更新日[：:]\s*(\d{4}/\d{1,2}/\d{1,2})',
        r'(\d{4}年\d{1,2}月\d{1,2}日)\s*更新',
        r'(\d{4}-\d{2}-\d{2})',
    ]

    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            date_str = match.group(1)
            # 日付を統一形式に変換
            try:
                if '年' in date_str:
                    date_str = date_str.replace('年', '-').replace('月', '-').replace('日', '')
                elif '/' in date_str:
                    date_str = date_str.replace('/', '-')
                return date_str
            except:
                return date_str

    # metaタグから取得を試みる
    meta_modified = soup.find("meta", {"name": "lastmod"}) or soup.find("meta", {"property": "article:modified_time"})
    if meta_modified and meta_modified.get("content"):
        return meta_modified["content"][:10]

    return None


def extract_info(html: str, page_config: Dict[str, Any]) -> Dict[str, Any]:
    """ページから情報を抽出"""
    soup = BeautifulSoup(html, "html.parser")

    # タイトル取得
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # メインコンテンツからテキスト抽出
    main = soup.find("main") or soup.find("div", {"id": "content"}) or soup.find("body")
    text = main.get_text(" ", strip=True) if main else ""

    # 更新日を抽出
    update_date = extract_update_date(soup, text)

    # キーワードマッチング
    matched_keywords = []
    for keyword in page_config.get("keywords", []):
        if keyword in text:
            matched_keywords.append(keyword)

    return {
        "title": title,
        "url": page_config["url"],
        "prefecture": page_config.get("prefecture", ""),
        "organization": page_config.get("organization", ""),
        "snippet": text[:200] + "..." if len(text) > 200 else text,
        "matched_keywords": matched_keywords,
        "update_date": update_date,
        "source": "direct",
        "fetched_at": datetime.now().isoformat(),
    }


def fetch_all() -> List[Dict[str, Any]]:
    """全ての監視ページを取得"""
    results = []

    for page_config in WATCH_PAGES:
        url = page_config["url"]
        print(f"直接監視: {url}")

        html = fetch_page(url)
        if html:
            info = extract_info(html, page_config)
            if info["matched_keywords"]:
                results.append(info)
                print(f"  マッチ: {info['matched_keywords']}")
            else:
                print(f"  キーワードマッチなし")
        else:
            print(f"  取得失敗")

    print(f"直接監視: {len(results)}件の結果を取得")
    return results


if __name__ == "__main__":
    results = fetch_all()
    for r in results:
        print(f"\n=== {r['title']} ===")
        print(f"URL: {r['url']}")
        print(f"組織: {r['organization']}")
        print(f"マッチキーワード: {r['matched_keywords']}")
        print(f"概要: {r['snippet'][:100]}...")
