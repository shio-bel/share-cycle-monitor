"""統合スクリプト: 全てのAPIからデータを取得し、結果を保存・通知"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from typing import List, Dict, Any

from config import DATA_DIR, RESULTS_FILE, SEEN_URLS_FILE
from fetch_google import fetch_all as fetch_google
from fetch_kkj import fetch_all as fetch_kkj
from fetch_direct import fetch_all as fetch_direct
from notifier import notify_new_items


def load_json(filepath: str) -> Any:
    """JSONファイルを読み込み"""
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []


def save_json(filepath: str, data: Any) -> None:
    """JSONファイルに保存"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_seen_urls() -> set:
    """既出URLを読み込み"""
    data = load_json(SEEN_URLS_FILE)
    if isinstance(data, list):
        return set(data)
    return set()


def save_seen_urls(urls: set) -> None:
    """既出URLを保存"""
    save_json(SEEN_URLS_FILE, list(urls))


def deduplicate_by_url(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """URLで重複を排除（最新のものを保持）"""
    seen = {}
    for item in items:
        url = item.get("url", "")
        if url and url not in seen:
            seen[url] = item
    return list(seen.values())


def merge_results(
    google_results: List[Dict[str, Any]],
    kkj_results: List[Dict[str, Any]],
    seen_urls: set
) -> tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """結果を統合し、新規のみを抽出"""
    all_results = []
    new_results = []
    new_urls = set()

    # Google結果を追加
    for item in google_results:
        url = item.get("url", "")
        if url:
            all_results.append(item)
            if url not in seen_urls:
                new_results.append(item)
                new_urls.add(url)

    # 官公需API結果を追加（重複チェック）
    for item in kkj_results:
        url = item.get("url", "")
        if url and url not in new_urls:
            all_results.append(item)
            if url not in seen_urls:
                new_results.append(item)
                new_urls.add(url)

    return all_results, new_results


def main():
    """メイン処理"""
    print(f"=== シェアサイクル監視 実行開始: {datetime.now().isoformat()} ===")

    # 既出URLを読み込み
    seen_urls = load_seen_urls()
    print(f"既出URL数: {len(seen_urls)}")

    # 各APIからデータ取得
    print("\n--- Google Custom Search API ---")
    google_results = fetch_google()

    print("\n--- 官公需情報ポータルAPI ---")
    kkj_results = fetch_kkj()

    print("\n--- 直接監視 ---")
    direct_results = fetch_direct()

    # 結果を統合
    print("\n--- 結果統合 ---")
    # Google + 直接監視の結果を統合
    combined_google = google_results + direct_results
    all_results, new_results = merge_results(combined_google, kkj_results, seen_urls)
    print(f"全結果: {len(all_results)}件")
    print(f"新着: {len(new_results)}件")

    # 既存の結果を読み込んで統合
    existing_results = load_json(RESULTS_FILE)
    if isinstance(existing_results, list):
        # 新着を先頭に追加
        combined_results = new_results + existing_results
    else:
        combined_results = new_results

    # URLで重複を排除
    combined_results = deduplicate_by_url(combined_results)
    print(f"重複排除後: {len(combined_results)}件")

    # 結果を保存
    save_json(RESULTS_FILE, combined_results)
    print(f"結果を保存: {RESULTS_FILE}")

    # 既出URLを更新
    for item in all_results:
        url = item.get("url", "")
        if url:
            seen_urls.add(url)
    save_seen_urls(seen_urls)
    print(f"既出URL更新: {len(seen_urls)}件")

    # 新着があれば通知
    if new_results:
        print("\n--- メール通知 ---")
        notify_new_items(new_results)
    else:
        print("\n新着案件なし。通知をスキップ。")

    print(f"\n=== 処理完了: {datetime.now().isoformat()} ===")


if __name__ == "__main__":
    main()
