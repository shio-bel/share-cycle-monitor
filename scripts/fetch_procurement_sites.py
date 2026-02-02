"""入札王等の入札情報サイトをGoogle経由で横断検索"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from fetch_google import search_google, parse_search_result, extract_prefecture


def fetch_all(site_queries: Dict[str, List[str]]) -> List[Dict[str, Any]]:
    """入札サイトをGoogle経由で検索（njss以外）"""
    all_results = []
    seen_urls = set()

    for site_name, queries in site_queries.items():
        if site_name == "njss":
            continue  # NJSSはfetch_njssで処理
        for query in queries:
            print(f"検索中: {query}")
            items = search_google(query)
            for item in items:
                url = item.get("link", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    result = parse_search_result(item)
                    result["source"] = site_name
                    result["prefecture"] = extract_prefecture(
                        result["title"] + result["snippet"] + url
                    )
                    all_results.append(result)

    print(f"入札サイト検索: {len(all_results)}件の結果を取得")
    return all_results
