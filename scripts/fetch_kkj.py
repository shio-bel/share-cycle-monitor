"""官公需情報ポータルサイトAPIを使用して入札情報を取得"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from typing import List, Dict, Any
from config import KANTO_LG_CODES


# 官公需API エンドポイント
KKJ_API_URL = "https://www.kkj.go.jp/api/v1/"


def search_kkj(query: str, lg_codes: List[str] = None) -> List[Dict[str, Any]]:
    """官公需APIで検索を実行"""
    # APIエンドポイントのURLを構築
    # 参考: https://www.kkj.go.jp/doc/ja/api_guide.pdf
    params = {
        "Query": query,
    }

    # 地域コードを追加
    if lg_codes:
        params["LG_Code"] = ",".join(lg_codes)

    # 過去30日の公告を対象
    today = datetime.now()
    start_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    end_date = today.strftime("%Y-%m-%d")
    params["CFT_Issue_Date"] = f"{start_date}/{end_date}"

    try:
        response = requests.get(KKJ_API_URL, params=params, timeout=30)
        response.raise_for_status()
        return parse_xml_response(response.text)
    except requests.exceptions.RequestException as e:
        print(f"官公需API エラー: {e}")
        return []


def parse_xml_response(xml_text: str) -> List[Dict[str, Any]]:
    """XMLレスポンスを解析"""
    results = []
    try:
        root = ET.fromstring(xml_text)
        for result in root.findall(".//SearchResult"):
            item = {
                "title": get_xml_text(result, "ProjectName"),
                "url": get_xml_text(result, "ExternalDocumentURI"),
                "organization": get_xml_text(result, "OrganizationName"),
                "prefecture": get_xml_text(result, "PrefectureName"),
                "category": get_xml_text(result, "Category"),
                "issue_date": get_xml_text(result, "CftIssueDate"),
                "deadline": get_xml_text(result, "PeriodEndTime"),
                "source": "kkj",
                "fetched_at": datetime.now().isoformat(),
            }
            if item["title"] and item["url"]:
                results.append(item)
    except ET.ParseError as e:
        print(f"XML解析エラー: {e}")
    return results


def get_xml_text(element: ET.Element, tag: str) -> str:
    """XMLエレメントからテキストを取得"""
    child = element.find(tag)
    return child.text if child is not None and child.text else ""


def fetch_all() -> List[Dict[str, Any]]:
    """シェアサイクル関連の入札情報を取得"""
    all_results = []
    seen_urls = set()

    # 検索キーワード
    queries = ["自転車", "シェアサイクル", "サイクル", "サイクルポート"]

    for query in queries:
        print(f"官公需API検索中: {query}")
        items = search_kkj(query, KANTO_LG_CODES)
        for item in items:
            url = item.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_results.append(item)

    print(f"官公需API: {len(all_results)}件の結果を取得")
    return all_results


if __name__ == "__main__":
    results = fetch_all()
    for r in results[:5]:
        print(f"- {r['title']}")
        print(f"  発注機関: {r['organization']}")
        print(f"  URL: {r['url']}")
        print()
