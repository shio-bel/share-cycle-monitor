"""Google Custom Search APIを使用して自治体サイトからシェアサイクル関連情報を検索"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional
from config import GOOGLE_API_KEY, GOOGLE_CSE_ID, SEARCH_QUERIES, KANTO_KEYWORDS

# 月名を数字に変換
MONTH_MAP = {
    'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
    'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
    'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
}


def search_google(query: str, start: int = 1) -> List[Dict[str, Any]]:
    """Google Custom Search APIで検索を実行"""
    if not GOOGLE_API_KEY or not GOOGLE_CSE_ID:
        print("警告: GOOGLE_API_KEY または GOOGLE_CSE_ID が設定されていません")
        return []

    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CSE_ID,
        "q": query,
        "start": start,
        "num": 10,  # 最大10件
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("items", [])
    except requests.exceptions.RequestException as e:
        print(f"Google検索エラー: {e}")
        return []


def extract_date_from_snippet(snippet: str) -> Optional[str]:
    """snippetから更新日を抽出"""
    # パターン1: "Dec 4, 2025" 形式（Google検索結果でよく見る）
    match = re.match(r'^([A-Z][a-z]{2})\s+(\d{1,2}),\s+(\d{4})', snippet)
    if match:
        month = MONTH_MAP.get(match.group(1), '01')
        day = match.group(2).zfill(2)
        year = match.group(3)
        return f"{year}-{month}-{day}"

    # パターン2: "2025年12月24日" 形式
    match = re.search(r'(\d{4})年(\d{1,2})月(\d{1,2})日', snippet)
    if match:
        return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"

    # パターン3: "2025/12/24" 形式
    match = re.search(r'(\d{4})/(\d{1,2})/(\d{1,2})', snippet)
    if match:
        return f"{match.group(1)}-{match.group(2).zfill(2)}-{match.group(3).zfill(2)}"

    return None


def parse_search_result(item: Dict[str, Any]) -> Dict[str, Any]:
    """検索結果を解析して標準形式に変換"""
    snippet = item.get("snippet", "")
    update_date = extract_date_from_snippet(snippet)

    return {
        "title": item.get("title", ""),
        "url": item.get("link", ""),
        "snippet": snippet,
        "update_date": update_date,
        "source": "google",
        "fetched_at": datetime.now().isoformat(),
    }


def extract_prefecture(text: str) -> str:
    """テキストから都道府県を抽出"""
    for keyword in KANTO_KEYWORDS:
        if keyword in text:
            return keyword
    return ""


def fetch_all() -> List[Dict[str, Any]]:
    """全ての検索クエリを実行して結果を収集"""
    all_results = []
    seen_urls = set()

    for query in SEARCH_QUERIES:
        # site:*.lg.jp を追加して自治体サイトに限定
        full_query = f"site:*.lg.jp {query}"
        print(f"検索中: {full_query}")

        items = search_google(full_query)
        for item in items:
            url = item.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                result = parse_search_result(item)
                # 都道府県を抽出
                result["prefecture"] = extract_prefecture(
                    result["title"] + result["snippet"] + url
                )
                all_results.append(result)

    print(f"Google検索: {len(all_results)}件の結果を取得")
    return all_results


if __name__ == "__main__":
    results = fetch_all()
    for r in results[:5]:
        print(f"- {r['title']}")
        print(f"  URL: {r['url']}")
        print(f"  都道府県: {r['prefecture']}")
        print()
