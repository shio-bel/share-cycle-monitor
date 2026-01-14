"""メール通知機能"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import List, Dict, Any
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, NOTIFY_EMAIL


def is_within_24h(date_str: str) -> bool:
    """更新日が過去24時間以内かチェック"""
    if not date_str:
        return False
    try:
        # YYYY-MM-DD形式を想定
        update_date = datetime.strptime(date_str[:10], "%Y-%m-%d")
        now = datetime.now()
        return (now - update_date) <= timedelta(hours=24)
    except (ValueError, TypeError):
        return False


def send_email(subject: str, body: str) -> bool:
    """メールを送信"""
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD or not NOTIFY_EMAIL:
        print("警告: メール設定が不完全です。通知をスキップします。")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = NOTIFY_EMAIL
        msg["Subject"] = subject

        msg.attach(MIMEText(body, "plain", "utf-8"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.send_message(msg)

        print(f"メール送信成功: {NOTIFY_EMAIL}")
        return True
    except Exception as e:
        print(f"メール送信エラー: {e}")
        return False


def sort_by_date(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """更新日が新しい順にソート（日付なしは最後）"""
    def get_date_key(item):
        date_str = item.get("update_date") or ""
        if not date_str:
            return ""  # 日付なしは空文字（最後になる）
        return date_str

    return sorted(items, key=get_date_key, reverse=True)


def notify_new_items(items: List[Dict[str, Any]], seen_urls: set = None) -> bool:
    """新着案件を通知（過去24時間以内の更新のみ）"""
    if not items:
        print("新着案件なし。通知をスキップします。")
        return False

    seen_urls = seen_urls or set()

    # 過去24時間以内の更新のみをフィルタ
    recent_items = [item for item in items if is_within_24h(item.get("update_date"))]

    if not recent_items:
        print("過去24時間以内の更新案件なし。通知をスキップします。")
        return False

    # 更新日が新しい順にソート
    sorted_items = sort_by_date(recent_items)

    # 新着と既報をカウント
    new_count = sum(1 for item in sorted_items if item.get("url") not in seen_urls)
    repeat_count = len(sorted_items) - new_count

    subject = f"[シェアサイクル監視] 更新案件: {len(sorted_items)}件（新着{new_count}/既報{repeat_count}）"

    body_lines = [
        "過去24時間以内に更新されたシェアサイクル関連案件です。",
        "",
        "=" * 50,
    ]

    for i, item in enumerate(sorted_items, 1):
        url = item.get("url", "")
        is_new = url not in seen_urls
        status = "★新着★" if is_new else "【既報】"

        body_lines.append(f"\n{status} 案件{i}")
        body_lines.append(f"タイトル: {item.get('title', '不明')}")
        if item.get("organization"):
            body_lines.append(f"発注機関: {item['organization']}")
        if item.get("prefecture"):
            body_lines.append(f"都道府県: {item['prefecture']}")
        if item.get("update_date"):
            body_lines.append(f"記事更新日: {item['update_date']}")
        if item.get("deadline"):
            body_lines.append(f"締切日: {item['deadline']}")
        body_lines.append(f"URL: {url}")
        body_lines.append("-" * 30)

    body_lines.append("")
    body_lines.append("詳細はダッシュボードをご確認ください。")
    body_lines.append("https://share-cycle-monitor.vercel.app")

    body = "\n".join(body_lines)
    return send_email(subject, body)


if __name__ == "__main__":
    # テスト用
    test_items = [
        {
            "title": "テスト案件",
            "url": "https://example.com",
            "organization": "テスト自治体",
            "prefecture": "東京",
            "deadline": "2025-02-01",
        }
    ]
    notify_new_items(test_items)
