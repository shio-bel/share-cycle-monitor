"""重要なページを直接監視するスクリプト"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any

# 直接監視するページのリスト
WATCH_PAGES = [
    {
        "url": "https://www.city.sumida.lg.jp/kurashi/jitensha/bicycle/share_cycle.html",
        "prefecture": "東京",
        "organization": "墨田区",
        "keywords": ["シェアサイクル", "公募", "募集", "事業者"],
    },
    # 必要に応じて追加
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


def extract_info(html: str, page_config: Dict[str, Any]) -> Dict[str, Any]:
    """ページから情報を抽出"""
    soup = BeautifulSoup(html, "html.parser")

    # タイトル取得
    title_tag = soup.find("title")
    title = title_tag.get_text(strip=True) if title_tag else ""

    # メインコンテンツからテキスト抽出
    main = soup.find("main") or soup.find("div", {"id": "content"}) or soup.find("body")
    text = main.get_text(" ", strip=True) if main else ""

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
