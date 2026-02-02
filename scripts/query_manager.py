"""クエリ自動生成・クォータ管理・ローテーション"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from datetime import datetime
from typing import Dict, List, Any

from config import (
    TOPICS, ACTIONS, EVENT_QUERIES, PROCUREMENT_SITES,
    QUOTA, QUERY_STATE_FILE, DATA_DIR,
)


def _generate_all_combinations() -> List[str]:
    """トピック × アクション の全組み合わせを生成"""
    return [f"{t['term']} {a['term']}" for t in TOPICS for a in ACTIONS]


def _load_state() -> Dict[str, Any]:
    """クエリ実行状態を読み込み"""
    if os.path.exists(QUERY_STATE_FILE):
        with open(QUERY_STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_state(state: Dict[str, Any]) -> None:
    """クエリ実行状態を保存"""
    os.makedirs(os.path.dirname(QUERY_STATE_FILE), exist_ok=True)
    with open(QUERY_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def _priority_score(query: str, state: Dict[str, Any], now: datetime) -> float:
    """クエリの優先度スコアを算出"""
    topic_weight = 0
    action_weight = 0
    for t in TOPICS:
        if t["term"] in query:
            topic_weight = t["weight"]
            break
    for a in ACTIONS:
        if a["term"] in query:
            action_weight = a["weight"]
            break

    # 未実行日数ボーナス
    last_run = state.get(query, {}).get("last_run")
    if last_run:
        days_since = (now - datetime.fromisoformat(last_run)).total_seconds() / 86400
    else:
        days_since = 30  # 未実行は30日相当のボーナス

    return topic_weight + action_weight + days_since * 0.5


def select_queries_for_run() -> Dict[str, List[str]]:
    """今回実行するクエリを選択し、状態を更新"""
    state = _load_state()
    now = datetime.now()
    alloc = QUOTA["allocation"]

    # --- Google一般検索 ---
    all_combos = _generate_all_combinations()
    scored = [(q, _priority_score(q, state, now)) for q in all_combos]
    scored.sort(key=lambda x: x[1], reverse=True)
    google_queries = [q for q, _ in scored[:alloc["google"]]]

    # --- 入札サイト検索 ---
    site_queries: Dict[str, List[str]] = {}
    for site in PROCUREMENT_SITES:
        name = site["name"]
        domain = site["domain"]
        limit = alloc.get(name, 4)
        # トピックのみ（アクション不要、サイト自体が入札情報）
        topic_scored = []
        for t in TOPICS:
            q = f"site:{domain} {t['term']}"
            last_run = state.get(q, {}).get("last_run")
            if last_run:
                days_since = (now - datetime.fromisoformat(last_run)).total_seconds() / 86400
            else:
                days_since = 30
            score = t["weight"] + days_since * 0.5
            topic_scored.append((q, score))
        topic_scored.sort(key=lambda x: x[1], reverse=True)
        site_queries[name] = [q for q, _ in topic_scored[:limit]]

    # --- イベント固有クエリ ---
    event_scored = []
    for q in EVENT_QUERIES:
        last_run = state.get(q, {}).get("last_run")
        if last_run:
            days_since = (now - datetime.fromisoformat(last_run)).total_seconds() / 86400
        else:
            days_since = 30
        event_scored.append((q, days_since))
    event_scored.sort(key=lambda x: x[1], reverse=True)
    event_queries = [q for q, _ in event_scored[:alloc["event"]]]

    # 状態を更新
    now_iso = now.isoformat()
    all_selected = google_queries + event_queries
    for queries in site_queries.values():
        all_selected += queries
    for q in all_selected:
        state[q] = {"last_run": now_iso}
    _save_state(state)

    total = len(all_selected)
    print(f"クエリ選択完了: {total}件 (上限{QUOTA['per_run']})")

    return {
        "google": google_queries + event_queries,
        **site_queries,
    }


if __name__ == "__main__":
    selected = select_queries_for_run()
    for category, queries in selected.items():
        print(f"\n[{category}] ({len(queries)}件)")
        for q in queries:
            print(f"  - {q}")
    total = sum(len(v) for v in selected.values())
    print(f"\n合計: {total}件")
