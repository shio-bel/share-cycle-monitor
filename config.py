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

# 検索トピック（組み合わせ自動生成の基盤）
# weight: 優先度スコア（高いほど頻繁に検索される）
TOPICS = [
    {"term": "シェアサイクル", "weight": 10},
    {"term": "自転車シェアリング", "weight": 8},
    {"term": "コミュニティサイクル", "weight": 7},
    {"term": "サイクルポート", "weight": 6},
    {"term": "シェアリング自転車", "weight": 5},
    {"term": "電動キックボード", "weight": 8},
    {"term": "特定小型原動機付自転車", "weight": 6},
    {"term": "マイクロモビリティ", "weight": 7},
]

ACTIONS = [
    {"term": "公募", "weight": 10},
    {"term": "入札", "weight": 9},
    {"term": "募集", "weight": 8},
    {"term": "事業者", "weight": 8},
    {"term": "プロポーザル", "weight": 7},
    {"term": "企画提案", "weight": 7},
    {"term": "事業者選定", "weight": 7},
    {"term": "協定", "weight": 5},
    {"term": "連携", "weight": 5},
    {"term": "スポンサー", "weight": 4},
    {"term": "実証実験", "weight": 6},
    {"term": "用地", "weight": 4},
]

# イベント固有クエリ（期間限定で追加・削除）
EVENT_QUERIES = [
    "横浜万博 シェアサイクル",
    "EXPO2027 シェアサイクル",
    "園芸博 シェアサイクル",
    "横浜万博 電動キックボード",
]

# 入札情報サイト（site:指定でGoogle検索）
PROCUREMENT_SITES = [
    {"name": "njss", "domain": "njss.info"},
    {"name": "nyusatsu-king", "domain": "nyusatsu-king.com"},
]

# クォータ設定（Google CSE無料枠 = 100クエリ/日）
QUOTA = {
    "daily_limit": 100,
    "runs_per_day": 4,
    "per_run": 25,
    "allocation": {
        "google": 13,
        "njss": 4,
        "nyusatsu-king": 4,
        "event": 4,
    },
}

# 監視対象地域のLGコード（都道府県コード）
TARGET_LG_CODES = [
    # 関東地方
    "08",  # 茨城県
    "09",  # 栃木県
    "10",  # 群馬県
    "11",  # 埼玉県
    "12",  # 千葉県
    "13",  # 東京都
    "14",  # 神奈川県
    # 沖縄県
    "47",  # 沖縄県
]
# 後方互換性のため
KANTO_LG_CODES = TARGET_LG_CODES

# 地域キーワード
TARGET_KEYWORDS = ["東京", "神奈川", "埼玉", "千葉", "茨城", "栃木", "群馬", "沖縄", "那覇", "石垣"]
# 後方互換性のため
KANTO_KEYWORDS = TARGET_KEYWORDS

# データファイルパス
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
RESULTS_FILE = os.path.join(DATA_DIR, "results.json")
SEEN_URLS_FILE = os.path.join(DATA_DIR, "seen_urls.json")
QUERY_STATE_FILE = os.path.join(DATA_DIR, "query_state.json")
