"""メール通知機能"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any
from config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD, NOTIFY_EMAIL


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


def notify_new_items(items: List[Dict[str, Any]]) -> bool:
    """新着案件を通知"""
    if not items:
        print("新着案件なし。通知をスキップします。")
        return False

    # 更新日が新しい順にソート
    sorted_items = sort_by_date(items)

    subject = f"[シェアサイクル監視] 新着案件: {len(sorted_items)}件"

    body_lines = [
        "シェアサイクル関連の新着案件が見つかりました。",
        "",
        "=" * 50,
    ]

    for i, item in enumerate(sorted_items, 1):
        body_lines.append(f"\n【案件{i}】")
        body_lines.append(f"タイトル: {item.get('title', '不明')}")
        if item.get("organization"):
            body_lines.append(f"発注機関: {item['organization']}")
        if item.get("prefecture"):
            body_lines.append(f"都道府県: {item['prefecture']}")
        if item.get("update_date"):
            body_lines.append(f"記事更新日: {item['update_date']}")
        if item.get("deadline"):
            body_lines.append(f"締切日: {item['deadline']}")
        body_lines.append(f"URL: {item.get('url', '')}")
        body_lines.append("-" * 30)

    body_lines.append("")
    body_lines.append("詳細はダッシュボードをご確認ください。")

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
