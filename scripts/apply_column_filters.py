import re

file_path = r"C:\Users\vinay\.gemini\Fyers_Hist\dashboards\03_Festival_Seasonality_Research.html"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# CSS addition for column manager panel & drag-drop styles
custom_css = """
        /* Column Customizer Panel & Table Controls */
        .column-control-panel {
            background: rgba(30, 41, 59, 0.95);
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 1.25rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(0,0,0,0.4);
        }
        .panel-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 1px solid var(--border-color);
        }
        .panel-title {
            font-size: 1rem;
            font-weight: 700;
            color: var(--accent-blue);
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }
        .table-selector-tabs {
            display: flex;
            gap: 0.5rem;
        }
        .tab-btn-tbl {
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid var(--border-color);
            color: var(--text-secondary);
            padding: 0.35rem 0.75rem;
            border-radius: 6px;
            font-size: 0.82rem;
            cursor: pointer;
            font-weight: 600;
            transition: all 0.2s;
        }
        .tab-btn-tbl.active {
            background: var(--accent-blue);
            color: #fff;
            border-color: var(--accent-blue);
        }
        .col-manager-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 1.25rem;
        }
        @media (max-width: 768px) {
            .col-manager-grid { grid-template-columns: 1fr; }
        }
        .col-box {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 0.85rem;
        }
        .col-box-title {
            font-size: 0.82rem;
            font-weight: 700;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 0.75rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .col-list {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            min-height: 45px;
        }
        .col-chip {
            background: #334155;
            color: #f8fafc;
            border: 1px solid rgba(255,255,255,0.1);
            padding: 0.35rem 0.7rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 500;
            cursor: grab;
            display: inline-flex;
            align-items: center;
            gap: 0.4rem;
            user-select: none;
            transition: transform 0.15s, background-color 0.15s;
        }
        .col-chip:active { cursor: grabbing; }
        .col-chip.default-chip {
            background: rgba(56, 189, 248, 0.2);
            color: var(--accent-blue);
            border-color: rgba(56, 189, 248, 0.4);
            cursor: default;
        }
        .col-chip:hover:not(.default-chip) {
            background: #475569;
            transform: translateY(-1px);
        }
        .chip-remove, .chip-add {
            font-weight: bold;
            cursor: pointer;
            padding: 0 0.2rem;
            border-radius: 50%;
        }
        .chip-remove:hover { color: #f87171; }
        .chip-add:hover { color: #4ade80; }
        
        /* Drag reorder headers */
        th.draggable-th {
            cursor: grab;
            position: relative;
        }
        th.draggable-th:active { cursor: grabbing; }
        th.drag-over {
            border-left: 3px solid var(--accent-amber) !important;
            background: rgba(251, 191, 36, 0.15) !important;
        }
        .drag-handle {
            font-size: 0.75rem;
            opacity: 0.5;
            margin-right: 0.3rem;
        }
"""

content = content.replace("</style>", custom_css + "\n    </style>")

# Add the Column Customizer HTML Panel right after the global action bar
panel_html = """
        <!-- Dynamic Column Manager & Filter Section -->
        <div class="column-control-panel">
            <div class="panel-header">
                <div class="panel-title">
                    ⚙️ Dynamic Column & Order Customizer
                    <span style="font-size: 0.78rem; font-weight: normal; color: var(--text-secondary); margin-left: 0.5rem;">(Select optional columns or drag headers directly in tables to reorder)</span>
                </div>
                <div class="table-selector-tabs">
                    <button class="tab-btn-tbl active" onclick="switchTableTab(1)">Table 1: Day 0</button>
                    <button class="tab-btn-tbl" onclick="switchTableTab(2)">Table 2: Pre-Event (T-4..T-1)</button>
                    <button class="tab-btn-tbl" onclick="switchTableTab(3)">Table 3: Post-Event (T+1..T+4)</button>
                </div>
            </div>
            
            <div class="col-manager-grid">
                <!-- Visible Active Columns -->
                <div class="col-box">
                    <div class="col-box-title">
                        <span>Active Columns in <span id="active-table-label">Table 1</span></span>
                        <button onclick="resetTableColumns()" style="background:none; border:none; color:var(--accent-blue); font-size:0.75rem; cursor:pointer; text-decoration:underline;">Reset to Defaults</button>
                    </div>
                    <div class="col-list" id="active-cols-list">
                        <!-- Rendered by JS -->
                    </div>
                </div>
                
                <!-- Available Optional Columns -->
                <div class="col-box">
                    <div class="col-box-title">
                        <span>Available Extra Filters / Metrics</span>
                    </div>
                    <div class="col-list" id="available-cols-list">
                        <!-- Rendered by JS -->
                    </div>
                </div>
            </div>
        </div>
"""

content = content.replace("<!-- LEADERBOARD 1: LAST TRADING SESSION (DAY 0) -->", panel_html + "\n        <!-- LEADERBOARD 1: LAST TRADING SESSION (DAY 0) -->")

# Add the complete JavaScript logic for Column Configuration, Filtering, Drag-and-Drop Column Reordering
js_logic = """
        // ==========================================
        // DYNAMIC COLUMN MANAGEMENT & REORDER ENGINE
        // ==========================================

        const TABLE_COL_SPECS = {
            1: {
                defaultIds: ["rank", "event", "single_avg_ret", "win_rate", "worst_sess", "avg_low_high", "explore"],
                allCols: [
                    { id: "rank", label: "Rank", default: true },
                    { id: "event", label: "Festival / Holiday Event", default: true },
                    { id: "single_avg_ret", label: "Single-Day Avg Return", default: true },
                    { id: "win_rate", label: "Win Rate (Positive)", default: true },
                    { id: "std_dev", label: "Standard Dev (σ)", default: false },
                    { id: "gap_up", label: "Gap Up Open %", default: false },
                    { id: "best_sess", label: "Best Session (Max)", default: false },
                    { id: "worst_sess", label: "Worst Session (Min)", default: true },
                    { id: "lh_gt1", label: "Low-to-High % >1%", default: false },
                    { id: "lh_lt1", label: "Low-to-High % <1%", default: false },
                    { id: "avg_low_high", label: "Avg Low-to-High %", default: true },
                    { id: "max_low_high", label: "Max Low-to-High %", default: false },
                    { id: "min_low_high", label: "Min Low-to-High %", default: false },
                    { id: "explore", label: "Explore", default: true }
                ]
            },
            2: {
                defaultIds: ["rank", "event", "pre_avg_ret", "win_rate", "avg_4d_lh", "peak_vol", "explore"],
                allCols: [
                    { id: "rank", label: "Rank", default: true },
                    { id: "event", label: "Festival / Holiday Event", default: true },
                    { id: "pre_avg_ret", label: "Pre-Event Avg Return", default: true },
                    { id: "win_rate", label: "Win Rate (Positive)", default: true },
                    { id: "std_dev", label: "Standard Dev (σ)", default: false },
                    { id: "exp_ratio", label: "Expectancy Ratio", default: false },
                    { id: "pre_best", label: "Pre-Event Best (Max)", default: false },
                    { id: "pre_worst", label: "Pre-Event Worst (Min)", default: false },
                    { id: "lh4_gt1", label: "4d Low-to-High % >1%", default: false },
                    { id: "lh4_lt1", label: "4d Low-to-High % <1%", default: false },
                    { id: "avg_4d_lh", label: "Avg 4d Low-to-High %", default: true },
                    { id: "max_4d_lh", label: "Max 4d Low-to-High %", default: false },
                    { id: "min_4d_lh", label: "Min 4d Low-to-High %", default: false },
                    { id: "peak_vol", label: "Peak Volatility Session", default: true },
                    { id: "explore", label: "Explore", default: true }
                ]
            },
            3: {
                defaultIds: ["rank", "event", "post_avg_ret", "win_rate", "avg_4d_lh", "peak_vol", "explore"],
                allCols: [
                    { id: "rank", label: "Rank", default: true },
                    { id: "event", label: "Festival / Holiday Event", default: true },
                    { id: "post_avg_ret", label: "Post-Event Avg Return", default: true },
                    { id: "win_rate", label: "Win Rate (Positive)", default: true },
                    { id: "std_dev", label: "Standard Dev (σ)", default: false },
                    { id: "exp_ratio", label: "Expectancy Ratio", default: false },
                    { id: "post_best", label: "Post-Event Best (Max)", default: false },
                    { id: "post_worst", label: "Post-Event Worst (Min)", default: false },
                    { id: "lh4_gt1", label: "4d Low-to-High % >1%", default: false },
                    { id: "lh4_lt1", label: "4d Low-to-High % <1%", default: false },
                    { id: "avg_4d_lh", label: "Avg 4d Low-to-High %", default: true },
                    { id: "max_4d_lh", label: "Max 4d Low-to-High %", default: false },
                    { id: "min_4d_lh", label: "Min 4d Low-to-High %", default: false },
                    { id: "peak_vol", label: "Peak Volatility Session", default: true },
                    { id: "explore", label: "Explore", default: true }
                ]
            }
        };

        // Active State per table
        let currentTabTbl = 1;
        let tableActiveCols = {
            1: [...TABLE_COL_SPECS[1].defaultIds],
            2: [...TABLE_COL_SPECS[2].defaultIds],
            3: [...TABLE_COL_SPECS[3].defaultIds]
        };

        function initColumnManagement() {
            [1, 2, 3].forEach(tNum => {
                const table = document.getElementById("sortable-table-" + tNum);
                if (!table) return;

                // Tag existing headers and cells with col-id attributes
                const ths = table.querySelectorAll("thead tr th");
                const specs = TABLE_COL_SPECS[tNum].allCols;
                ths.forEach((th, idx) => {
                    if (specs[idx]) {
                        th.setAttribute("data-col-id", specs[idx].id);
                        th.classList.add("draggable-th");
                        th.draggable = true;
                    }
                });

                const rows = table.querySelectorAll("tbody tr");
                rows.forEach(r => {
                    const tds = r.querySelectorAll("td");
                    tds.forEach((td, idx) => {
                        if (specs[idx]) {
                            td.setAttribute("data-col-id", specs[idx].id);
                        }
                    });
                });

                // Attach drag & drop handlers to table headers
                attachHeaderDragHandlers(table, tNum);

                // Apply initial visibility
                applyColumnVisibility(tNum);
            });

            renderManagerPanel();
        }

        function switchTableTab(tNum) {
            currentTabTbl = tNum;
            document.querySelectorAll(".tab-btn-tbl").forEach((b, i) => {
                b.classList.toggle("active", (i + 1) === tNum);
            });
            document.getElementById("active-table-label").innerText = `Table ${tNum}`;
            renderManagerPanel();
        }

        function renderManagerPanel() {
            const tNum = currentTabTbl;
            const activeIds = tableActiveCols[tNum];
            const allCols = TABLE_COL_SPECS[tNum].allCols;

            const activeList = document.getElementById("active-cols-list");
            const availList = document.getElementById("available-cols-list");

            activeList.innerHTML = "";
            availList.innerHTML = "";

            // Render Active Chips
            activeIds.forEach(id => {
                const colInfo = allCols.find(c => c.id === id);
                if (!colInfo) return;

                const chip = document.createElement("div");
                chip.className = "col-chip" + (colInfo.default ? " default-chip" : "");
                chip.innerHTML = `<span class="drag-handle">⋮⋮</span> ${colInfo.label}` +
                    (!colInfo.default ? `<span class="chip-remove" onclick="removeColumn(${tNum}, '${id}')">×</span>` : "");
                activeList.appendChild(chip);
            });

            // Render Available Chips
            allCols.forEach(colInfo => {
                if (!activeIds.includes(colInfo.id)) {
                    const chip = document.createElement("div");
                    chip.className = "col-chip";
                    chip.style.background = "rgba(255,255,255,0.05)";
                    chip.style.borderColor = "var(--border-color)";
                    chip.innerHTML = `${colInfo.label} <span class="chip-add" onclick="addColumn(${tNum}, '${colInfo.id}')">+</span>`;
                    availList.appendChild(chip);
                }
            });
        }

        function addColumn(tNum, colId) {
            if (!tableActiveCols[tNum].includes(colId)) {
                // Insert before 'explore' if present, otherwise push
                const exploreIdx = tableActiveCols[tNum].indexOf("explore");
                if (exploreIdx !== -1) {
                    tableActiveCols[tNum].splice(exploreIdx, 0, colId);
                } else {
                    tableActiveCols[tNum].push(colId);
                }
                applyColumnVisibility(tNum);
                renderManagerPanel();
            }
        }

        function removeColumn(tNum, colId) {
            const colInfo = TABLE_COL_SPECS[tNum].allCols.find(c => c.id === colId);
            if (colInfo && colInfo.default) return; // Prevent removing defaults

            tableActiveCols[tNum] = tableActiveCols[tNum].filter(id => id !== colId);
            applyColumnVisibility(tNum);
            renderManagerPanel();
        }

        function resetTableColumns() {
            const tNum = currentTabTbl;
            tableActiveCols[tNum] = [...TABLE_COL_SPECS[tNum].defaultIds];
            applyColumnVisibility(tNum);
            renderManagerPanel();
        }

        function applyColumnVisibility(tNum) {
            const table = document.getElementById("sortable-table-" + tNum);
            if (!table) return;

            const activeIds = tableActiveCols[tNum];

            // Show/Hide headers & reorder DOM elements according to activeIds order
            const theadRow = table.querySelector("thead tr");
            const allThs = Array.from(theadRow.querySelectorAll("th"));
            
            // First hide all
            allThs.forEach(th => th.style.display = "none");

            // Re-append active THs in order of activeIds
            activeIds.forEach(id => {
                const th = allThs.find(t => t.getAttribute("data-col-id") === id);
                if (th) {
                    th.style.display = "";
                    theadRow.appendChild(th);
                }
            });

            // Do same for each TD in tbody
            const tbodyRows = table.querySelectorAll("tbody tr");
            tbodyRows.forEach(row => {
                const allTds = Array.from(row.querySelectorAll("td"));
                allTds.forEach(td => td.style.display = "none");

                activeIds.forEach(id => {
                    const td = allTds.find(t => t.getAttribute("data-col-id") === id);
                    if (td) {
                        td.style.display = "";
                        row.appendChild(td);
                    }
                });
            });
        }

        // Drag and Drop Header Reordering
        let draggedColId = null;

        function attachHeaderDragHandlers(table, tNum) {
            const thead = table.querySelector("thead");

            thead.addEventListener("dragstart", (e) => {
                const th = e.target.closest("th");
                if (!th) return;
                draggedColId = th.getAttribute("data-col-id");
                e.dataTransfer.effectAllowed = "move";
            });

            thead.addEventListener("dragover", (e) => {
                e.preventDefault();
                const th = e.target.closest("th");
                if (th && th.getAttribute("data-col-id") !== draggedColId) {
                    th.classList.add("drag-over");
                }
            });

            thead.addEventListener("dragleave", (e) => {
                const th = e.target.closest("th");
                if (th) th.classList.remove("drag-over");
            });

            thead.addEventListener("drop", (e) => {
                e.preventDefault();
                const th = e.target.closest("th");
                if (th) {
                    th.classList.remove("drag-over");
                    const targetColId = th.getAttribute("data-col-id");
                    if (draggedColId && targetColId && draggedColId !== targetColId) {
                        reorderActiveColumns(tNum, draggedColId, targetColId);
                    }
                }
                draggedColId = null;
            });
        }

        function reorderActiveColumns(tNum, srcId, targetId) {
            const list = tableActiveCols[tNum];
            const srcIdx = list.indexOf(srcId);
            const tgtIdx = list.indexOf(targetId);

            if (srcIdx !== -1 && tgtIdx !== -1) {
                list.splice(srcIdx, 1);
                list.splice(tgtIdx, 0, srcId);
                applyColumnVisibility(tNum);
                renderManagerPanel();
            }
        }

        // Initialize on DOM load
        document.addEventListener("DOMContentLoaded", () => {
            initColumnManagement();
        });
"""

# Insert JS logic before closing script tag
content = content.replace("    </script>\n</body>", js_logic + "\n    </script>\n</body>")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Updated dashboards/03_Festival_Seasonality_Research.html successfully!")
