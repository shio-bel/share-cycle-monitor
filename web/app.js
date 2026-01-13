// シェアサイクル監視ダッシュボード

let allData = [];
let filteredData = [];

// データ読み込み
async function loadData() {
    try {
        const response = await fetch('../data/results.json');
        if (!response.ok) {
            throw new Error('データの読み込みに失敗しました');
        }
        allData = await response.json();
        filteredData = allData;
        updateStats();
        renderResults();
    } catch (error) {
        console.error('Error:', error);
        document.getElementById('results').innerHTML = `
            <div class="no-results">
                <p>データの読み込みに失敗しました。</p>
                <p>まだデータが取得されていないか、ファイルが見つかりません。</p>
            </div>
        `;
    }
}

// 統計情報更新
function updateStats() {
    const totalCount = document.getElementById('total-count');
    const newCount = document.getElementById('new-count');
    const lastUpdate = document.getElementById('last-update');

    totalCount.textContent = allData.length;

    // 24時間以内の新着をカウント
    const now = new Date();
    const oneDayAgo = new Date(now - 24 * 60 * 60 * 1000);
    const newItems = allData.filter(item => {
        const fetchedAt = new Date(item.fetched_at);
        return fetchedAt > oneDayAgo;
    });
    newCount.textContent = newItems.length;

    // 最終更新日時
    if (allData.length > 0 && allData[0].fetched_at) {
        const date = new Date(allData[0].fetched_at);
        lastUpdate.textContent = formatDate(date);
    } else {
        lastUpdate.textContent = '-';
    }
}

// 日付フォーマット
function formatDate(date) {
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${month}/${day} ${hours}:${minutes}`;
}

// 24時間以内かチェック
function isNew(fetchedAt) {
    const now = new Date();
    const oneDayAgo = new Date(now - 24 * 60 * 60 * 1000);
    return new Date(fetchedAt) > oneDayAgo;
}

// 結果表示
function renderResults() {
    const container = document.getElementById('results');

    if (filteredData.length === 0) {
        container.innerHTML = `
            <div class="no-results">
                <p>該当する案件が見つかりませんでした。</p>
            </div>
        `;
        return;
    }

    const html = filteredData.map(item => {
        const isNewItem = isNew(item.fetched_at);
        const sourceLabel = item.source === 'google' ? 'Google' : '官公需';

        return `
            <article class="result-card ${isNewItem ? 'new' : ''}">
                <div class="result-header">
                    <h2 class="result-title">
                        <a href="${escapeHtml(item.url)}" target="_blank" rel="noopener noreferrer">
                            ${escapeHtml(item.title || '無題')}
                        </a>
                    </h2>
                    <div class="result-badges">
                        ${isNewItem ? '<span class="badge badge-new">NEW</span>' : ''}
                        ${item.prefecture ? `<span class="badge badge-prefecture">${escapeHtml(item.prefecture)}</span>` : ''}
                        <span class="badge badge-source">${sourceLabel}</span>
                    </div>
                </div>
                <div class="result-meta">
                    ${item.organization ? `<span>発注機関: ${escapeHtml(item.organization)}</span>` : ''}
                    ${item.deadline ? `<span>締切: ${escapeHtml(item.deadline)}</span>` : ''}
                    ${item.fetched_at ? `<span>取得: ${formatDate(new Date(item.fetched_at))}</span>` : ''}
                </div>
                ${item.snippet ? `<p class="result-snippet">${escapeHtml(item.snippet)}</p>` : ''}
            </article>
        `;
    }).join('');

    container.innerHTML = html;
}

// HTMLエスケープ
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// フィルタリング
function filterData() {
    const searchQuery = document.getElementById('search').value.toLowerCase();
    const prefectureFilter = document.getElementById('prefecture').value;
    const sourceFilter = document.getElementById('source').value;

    filteredData = allData.filter(item => {
        // キーワード検索
        if (searchQuery) {
            const searchText = [
                item.title || '',
                item.organization || '',
                item.snippet || '',
                item.prefecture || ''
            ].join(' ').toLowerCase();
            if (!searchText.includes(searchQuery)) {
                return false;
            }
        }

        // 都道府県フィルター
        if (prefectureFilter && item.prefecture !== prefectureFilter) {
            return false;
        }

        // 情報源フィルター
        if (sourceFilter && item.source !== sourceFilter) {
            return false;
        }

        return true;
    });

    renderResults();
}

// イベントリスナー設定
document.getElementById('search').addEventListener('input', filterData);
document.getElementById('prefecture').addEventListener('change', filterData);
document.getElementById('source').addEventListener('change', filterData);

// 初期化
loadData();
