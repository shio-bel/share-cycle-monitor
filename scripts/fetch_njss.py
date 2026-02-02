"""NJSS（入札情報速報サービス）の案件をGoogle経由で検索"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from typing import List, Dict, Any
from fetch_google import search_google, parse_search_result, extract_prefecture


def fetch_all(queries: List[str] = None) -> List[Dict[str, Any]]:
    """NJSS案件をGoogle経由で検索。queriesはsite:njss.info付きのクエリリスト。"""
    if not queries:
        print("NJSS検索: クエリが指定されていません")
        return []

    all_results = []
    seen_urls = set()

    for query in queries:
        print(f"検索中: {query}")

        items = search_google(query)
        for item in items:
            url = item.get("link", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                result = parse_search_result(item)
                result["source"] = "njss"
                result["prefecture"] = extract_prefecture(
                    result["title"] + result["snippet"] + url
                )
                all_results.append(result)

    print(f"NJSS検索: {len(all_results)}件の結果を取得")
    return all_results


if __name__ == "__main__":
    results = fetch_all(["site:njss.info シェアサイクル"])
    for r in results[:5]:
        print(f"- {r['title']}")
        print(f"  URL: {r['url']}")
        print()
