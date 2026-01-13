"""設定ファイル"""
import os

# Google Custom Search API
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY", "")
GOOGLE_CSE_ID = os.environ.get("GOOGLE_CSE_ID", "")

# 官公需API
KKJ_API_URL = "https://www.kkj.go.jp/api/search"

# メール通知設定
GMAIL_ADDRESS = os.environ.get("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD", "")
NOTIFY_EMAIL = os.environ.get("NOTIFY_EMAIL", "")

# 検索設定
SEARCH_QUERIES = [
    "シェアサイクル 公募",
    "シェアサイクル 入札",
    "シェアサイクル 事業者",
    "シェアサイクル 募集",
    "自転車シェア 公募",
    "自転車シェア 入札",
    "サイクルポート 公募",
    "サイクルポート 事業者",
    "サイクルポート 募集",
    "シェアリング自転車 公募",
    "シェアサイクル 用地",
]

# 関東地方のLGコード（都道府県コード）
KANTO_LG_CODES = [
    "08",  # 茨城県
    "09",  # 栃木県
    "10",  # 群馬県
    "11",  # 埼玉県
    "12",  # 千葉県
    "13",  # 東京都
    "14",  # 神奈川県
]

# 地域キーワード
KANTO_KEYWORDS = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬"]

# データファイルパス
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")
SEEN_URLS_FILE = os.path.join(DATA_DIR, "seen_urls.json")
