"""重要なページを直接監視するスクリプト"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict, Any, Optional

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
