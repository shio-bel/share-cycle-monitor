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
        filteredData = [...allData];
        updateStats();
        sortData('update_desc');  // デフォルトで更新日順にソート
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
        lastUpdate.textContent = formatDateTime(date);
    } else {
        lastUpdate.textContent = '-';
    }
}

// 日付フォーマット（日時）
function formatDateTime(date) {
    const month = date.getMonth() + 1;
    const day = date.getDate();
    const hours = date.getHours().toString().padStart(2, '0');
    const minutes = date.getMinutes().toString().padStart(2, '0');
    return `${month}/${day} ${hours}:${minutes}`;
}

// 日付フォーマット（日付のみ）
function formatDate(dateStr) {
    if (!dateStr) return '';
    // YYYY-MM-DD形式を想定
    const parts = dateStr.split('-');
    if (parts.length === 3) {
        const year = parts[0];
        const month = parseInt(parts[1], 10);
        const day = parseInt(parts[2], 10);
        return `${year}/${month}/${day}`;
    }
    return dateStr;
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
        const sourceLabel = item.source === 'google' ? 'Google' : '直接監視';
        const updateDateFormatted = formatDate(item.update_date);

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
                        ${item.update_date ? `<span class="badge badge-date">更新: ${updateDateFormatted}</span>` : ''}
                        ${item.prefecture ? `<span class="badge badge-prefecture">${escapeHtml(item.prefecture)}</span>` : ''}
                        <span class="badge badge-source">${sourceLabel}</span>
                    </div>
                </div>
                <div class="result-meta">
                    ${item.organization ? `<span>発注機関: ${escapeHtml(item.organization)}</span>` : ''}
                    ${item.update_date ? `<span class="update-date">記事更新日: ${updateDateFormatted}</span>` : ''}
                    ${item.fetched_at ? `<span>取得: ${formatDateTime(new Date(item.fetched_at))}</span>` : ''}
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

// フィルタリングとソート
function filterData() {
    const searchQuery = document.getElementById('search').value.toLowerCase();
    const prefectureFilter = document.getElementById('prefecture').value;
    const sourceFilter = document.getElementById('source').value;
    const sortOption = document.getElementById('sort').value;

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

    // ソート
    sortData(sortOption);

    renderResults();
}

// ソート処理
function sortData(sortOption) {
    filteredData.sort((a, b) => {
        switch (sortOption) {
            case 'update_desc':
                // 更新日がないものは後ろに
                if (!a.update_date && !b.update_date) return 0;
                if (!a.update_date) return 1;
                if (!b.update_date) return -1;
                return new Date(b.update_date) - new Date(a.update_date);
            case 'update_asc':
                // 更新日がないものは後ろに
                if (!a.update_date && !b.update_date) return 0;
                if (!a.update_date) return 1;
                if (!b.update_date) return -1;
                return new Date(a.update_date) - new Date(b.update_date);
            default:
                // デフォルトは更新日（新しい順）
                if (!a.update_date && !b.update_date) return 0;
                if (!a.update_date) return 1;
                if (!b.update_date) return -1;
                return new Date(b.update_date) - new Date(a.update_date);
        }
    });
}

// イベントリスナー設定
document.getElementById('search').addEventListener('input', filterData);
document.getElementById('prefecture').addEventListener('change', filterData);
document.getElementById('source').addEventListener('change', filterData);
document.getElementById('sort').addEventListener('change', filterData);

// 初期化
loadData();
