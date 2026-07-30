// HMIE Visual Research Dashboard UI — App Logic (app.js)

document.addEventListener('DOMContentLoaded', () => {
    initTabs();
    loadRegimesAndBreadth();
    loadSectorRotation();
    loadStrategyLab();
    loadHistoricalEvidence();
    initAIBriefing();
});

// Global Chart Instances
let breadthChartInstance = null;
let sectorChartInstance = null;
let strategyChartInstance = null;

// Tab Switching Logic
function initTabs() {
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');

    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));

            btn.classList.add('active');
            const target = btn.getAttribute('data-tab');
            document.getElementById(target).classList.add('active');
        });
    });
}

// Load Regimes & Breadth Data
async function loadRegimesAndBreadth() {
    try {
        const res = await fetch('/api/v1/market-structure/regimes/current');
        if (!res.ok) return;
        const data = await res.json();

        const badge = document.getElementById('regime-badge');
        badge.textContent = data.regime_name;
        badge.className = `regime-badge-large ${data.regime_name}`;

        document.getElementById('regime-duration').textContent = `${data.duration_days} Days`;
        document.getElementById('regime-date').textContent = data.datetime;
        document.getElementById('breadth-ratio').textContent = data.breadth_ratio.toFixed(2);

        // Update Breadth Meters
        updateMeter('pct-ema20', data.pct_above_ema20);
        updateMeter('pct-ema50', data.pct_above_ema50);
        updateMeter('pct-ema200', data.pct_above_ema200);

        // Render Breadth Chart
        renderBreadthChart(data);

    } catch (err) {
        console.error('Failed to load regime data:', err);
    }
}

function updateMeter(id, val) {
    document.getElementById(`${id}-val`).textContent = `${val.toFixed(1)}%`;
    document.getElementById(`${id}-bar`).style.width = `${Math.min(100, Math.max(0, val))}%`;
}

function renderBreadthChart(currentData) {
    const ctx = document.getElementById('breadthChart').getContext('2d');
    if (breadthChartInstance) breadthChartInstance.destroy();

    breadthChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['EMA 20 Participation', 'EMA 50 Participation', 'EMA 200 Participation'],
            datasets: [{
                label: 'Market Participation Breadth (%)',
                data: [currentData.pct_above_ema20, currentData.pct_above_ema50, currentData.pct_above_ema200],
                backgroundColor: ['#38bdf8', '#a855f7', '#10b981'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { min: 0, max: 100, ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { ticks: { color: '#9ca3af' }, grid: { display: false } }
            }
        }
    });
}

// Load Sector Rotation Leaderboard & Chart
async function loadSectorRotation() {
    try {
        const res = await fetch('/api/v1/market-structure/rotation/sectors?limit=20');
        if (!res.ok) return;
        const data = await res.json();

        const tbody = document.getElementById('sector-table-body');
        tbody.innerHTML = '';

        const sectorNames = [];
        const sectorRS = [];

        data.data.forEach(item => {
            sectorNames.push(item.code);
            sectorRS.push(item.relative_strength_3m);

            const tr = document.createElement('tr');
            const deltaClass = item.rank_delta_63d >= 0 ? 'text-green' : 'text-red';
            const deltaSign = item.rank_delta_63d > 0 ? '+' : '';

            tr.innerHTML = `
                <td><strong>#${item.rank_3m}</strong></td>
                <td><strong>${item.code}</strong></td>
                <td>${item.relative_strength_3m.toFixed(2)}</td>
                <td class="${deltaClass}">${deltaSign}${item.rank_delta_63d} Ranks</td>
                <td><span class="status-badge ${item.status}">${item.status}</span></td>
            `;
            tbody.appendChild(tr);
        });

        renderSectorChart(sectorNames.slice(0, 10), sectorRS.slice(0, 10));
    } catch (err) {
        console.error('Failed to load sector rotation:', err);
    }
}

function renderSectorChart(labels, dataValues) {
    const ctx = document.getElementById('sectorChart').getContext('2d');
    if (sectorChartInstance) sectorChartInstance.destroy();

    sectorChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '3-Month Relative Strength Score',
                data: dataValues,
                backgroundColor: '#38bdf8',
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            indexAxis: 'y',
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                y: { ticks: { color: '#9ca3af' }, grid: { display: false } }
            }
        }
    });
}

// Load Stage 6 Strategy Lab & Chart
async function loadStrategyLab() {
    try {
        const res = await fetch('/api/v1/strategy/summary');
        if (!res.ok) return;
        const data = await res.json();

        const tbody = document.getElementById('strategy-table-body');
        tbody.innerHTML = '';

        const stratCodes = [];
        const stratCAGR = [];

        data.data.forEach(item => {
            stratCodes.push(item.strategy_code);
            stratCAGR.push(item.cagr_pct);

            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${item.strategy_code}</strong></td>
                <td>${item.strategy_name}</td>
                <td style="color: var(--accent-green); font-weight: 600;">+${item.cagr_pct.toFixed(2)}%</td>
                <td style="color: var(--accent-red);">${item.max_drawdown_pct.toFixed(2)}%</td>
                <td><strong>${item.sharpe_ratio.toFixed(2)}</strong></td>
                <td>${item.win_rate_pct.toFixed(1)}%</td>
                <td>${item.total_trades}</td>
            `;
            tbody.appendChild(tr);
        });

        renderStrategyChart(stratCodes, stratCAGR);
    } catch (err) {
        console.error('Failed to load strategy lab:', err);
    }
}

function renderStrategyChart(labels, dataValues) {
    const ctx = document.getElementById('strategyChart').getContext('2d');
    if (strategyChartInstance) strategyChartInstance.destroy();

    strategyChartInstance = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: '15-Year Backtest CAGR (%)',
                data: dataValues,
                backgroundColor: ['#38bdf8', '#a855f7', '#10b981'],
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { ticks: { color: '#9ca3af' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                x: { ticks: { color: '#9ca3af' }, grid: { display: false } }
            }
        }
    });
}

// Load Historical Evidence (Drawdowns & Macro Events)
async function loadHistoricalEvidence() {
    try {
        // Load Corrections
        const resCorr = await fetch('/api/v1/evidence/corrections');
        if (resCorr.ok) {
            const dataCorr = await resCorr.json();
            const tbodyCorr = document.getElementById('corrections-table-body');
            tbodyCorr.innerHTML = '';

            dataCorr.data.forEach(item => {
                const tr = document.createElement('tr');
                const recDaysText = item.recovery_days ? `${item.recovery_days} days` : 'N/A';
                const recDateText = item.recovery_date ? item.recovery_date : 'ONGOING';

                tr.innerHTML = `
                    <td><strong>${item.event_name}</strong></td>
                    <td>${item.peak_date}</td>
                    <td>${item.trough_date}</td>
                    <td>${recDateText}</td>
                    <td style="color: var(--accent-red); font-weight: 600;">${item.max_drawdown_pct.toFixed(2)}%</td>
                    <td>${item.correction_days}d</td>
                    <td>${recDaysText}</td>
                    <td><span class="status-badge ${item.recovery_type}">${item.recovery_type}</span></td>
                    <td><strong>${item.top_sector_60d}</strong></td>
                `;
                tbodyCorr.appendChild(tr);
            });
        }

        // Load Macro Events
        const resMacro = await fetch('/api/v1/evidence/macro-events');
        if (resMacro.ok) {
            const dataMacro = await resMacro.json();
            const tbodyMacro = document.getElementById('macro-table-body');
            tbodyMacro.innerHTML = '';

            dataMacro.data.forEach(item => {
                const tr = document.createElement('tr');
                const postClass = item.post_30d_market_return >= 0 ? 'text-green' : 'text-red';
                const postSign = item.post_30d_market_return > 0 ? '+' : '';

                tr.innerHTML = `
                    <td><strong>${item.event_name}</strong></td>
                    <td><span class="info-badge">${item.event_category}</span></td>
                    <td>${item.event_date}</td>
                    <td><span class="status-badge ${item.regime_at_event}">${item.regime_at_event}</span></td>
                    <td>${item.pre_30d_market_return >= 0 ? '+' : ''}${item.pre_30d_market_return.toFixed(2)}%</td>
                    <td class="${postClass}" style="font-weight: 600;">${postSign}${item.post_30d_market_return.toFixed(2)}%</td>
                    <td><strong>${item.top_sector_post_30d}</strong></td>
                `;
                tbodyMacro.appendChild(tr);
            });
        }

    } catch (err) {
        console.error('Failed to load evidence bank:', err);
    }
}

// AI Evidence Briefing Generation
function initAIBriefing() {
    const btn = document.getElementById('generate-ai-btn');
    const container = document.getElementById('ai-narrative-container');

    btn.addEventListener('click', async () => {
        btn.disabled = true;
        btn.textContent = '⌛ Generating Briefing...';
        container.innerHTML = '<p style="text-align: center; color: var(--text-muted); padding: 40px;">Querying precomputed REST endpoints and synthesizing research report...</p>';

        try {
            const res = await fetch('/api/v1/market-structure/ai/narrate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ focus_area: 'Overall Market Regimes & Evidence' })
            });

            if (!res.ok) throw new Error('API request failed');
            const data = await res.json();

            // Simple Markdown parser for display
            let md = data.markdown_narrative;
            md = md.replace(/^### (.*$)/gim, '<h3 style="color: var(--accent-blue); margin-top: 16px;">$1</h3>');
            md = md.replace(/^## (.*$)/gim, '<h2 style="color: var(--accent-blue); margin-top: 20px;">$1</h2>');
            md = md.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
            md = md.replace(/\n\n/g, '</p><p>');

            container.innerHTML = `<p>${md}</p>`;
        } catch (err) {
            container.innerHTML = `<p style="color: var(--accent-red);">Failed to generate narrative: ${err.message}</p>`;
        } finally {
            btn.disabled = false;
            btn.textContent = '⚡ Generate Live AI Briefing';
        }
    });
}
