[English version](README_EN.md)


# AI 智投顧問 (FinTech Trading AI)

專為非專業散戶投資者量身打造的量化策略與資產管理增強工具。本專案建基於輕量級架構，支援即時多股票數據抓取、量化指標（MACD、夏普比率、市盈率 P/E）計算、互動視覺化、SQLite 本地持久化數據庫以及 LLM 生成的專業投顧分析報告。全系統支援**中英雙語介面**，可於側邊欄一鍵即時切換。

---

## 🌟 三大增強功能之規劃與深度評估 (Three Features Evaluation)

### 1. 投資組合分析與夏普比率 (Portfolio Analytics & Sharpe Ratio)
* **需求痛點**：非專業投資者習慣單壓單一熱門股票，難以評估資產組合的整體性價比及非系統性風險。
* **技術方案**：引入多股票歷史收益率的協方差矩陣計算，動態計算自訂權重的組合預期年化收益率、年化波動率及夏普比率（Sharpe Ratio = (Rp − Rf) / σp）。
* **成效評估**：直觀呈現分散投資如何利用資產間的低相關性降低組合總體方差，提高散戶的風險意識。

### 2. 多維度策略：MACD 動量 + P/E 估值分位數
* **需求痛點**：散戶單看 MACD 容易在無量盤整或高估值泡沫期追高；單看 P/E 則容易陷入長年低迷的「價值陷阱」。
* **技術方案**：將技術指標（MACD 快慢線金叉/死叉、Histogram 柱狀動態）與基本面估值指標（Trailing/Forward P/E Ratio）融合，給出四種加權結論（強烈買入、投機性買入、左側吸納、減持觀望）。
* **成效評估**：大幅減少誤觸假突破信號的機率，為散戶提供具備安全邊際的技術信號。

### 3. LLM 智能投顧報告與 SQLite 數據庫整合
* **需求痛點**：複雜的量化數據對散戶存在門檻，同時缺乏簡易的持倉與交易動機複盤機制。
* **技術方案**：
  - **LLM 整合**：支援使用者輸入自訂 OpenAI API Key。若無提供 Key，系統亦自帶專業級別的啟發式財務規則解讀引擎（Fallback Heuristic Engine），保證零配置下即可生成香港金融語境的白話分析。內置 4 秒防逾時與代理伺服器異常自動攔截機制，確保系統絕不卡頓。
  - **SQLite 整合**：建立 `trading_app.db` 本地關係型資料庫，包含持倉管理（`portfolio`）與策略模擬日誌（`trade_history`）。
* **成效評估**：使決策有理有據，提升非專業用戶的長期投資紀律。

---

## 🚀 快速啟動指南

### 1. 安裝環境依賴

建議在 Python 3.10 或以上虛擬環境中運行：

    # 建立並啟用虛擬環境（可選但建議）
    python -m venv venv
    source venv/bin/activate        # macOS / Linux
    # venv\Scripts\activate         # Windows

    # 安裝所有依賴套件
    pip install -r requirements.txt

主要依賴套件（詳見 `requirements.txt`）：
* `streamlit` — 互動式網頁介面框架
* `yfinance` — 即時股票歷史數據與基本面資訊抓取
* `pandas` / `numpy` — 數據處理與量化計算核心
* `plotly` — 專業互動式 K 線圖、MACD 子圖及累計淨值走勢圖
* `openai` — LLM 智能投顧報告生成（可選，無 Key 亦可正常運行）
* `requests` — 網絡請求基礎支援

### 2. 啟動應用程式

在終端機（Terminal / CMD）輸入以下指令（注意：這是命令列指令，不是檔案名稱）：

    streamlit run app.py

執行後瀏覽器會自動開啟 http://localhost:8501，即可開始使用。

### 3. 首次使用

首次啟動時，系統會自動呼叫 `database.init_db()` 於專案根目錄建立 `trading_app.db` SQLite 數據庫檔案，無需任何手動設定或遷移腳本。

### 4. 介面語言切換 (Language Switching)

於側邊欄頂部的「🌐 Language / 語言」選項中選擇 **中文 (繁體)** 或 **English**，即可即時切換整個應用程式介面，包括：

* 所有分頁標題、按鈕、表單與提示訊息
* 策略訊號與估值評估文本（strategies.py 輸出）
* LLM / 專家規則引擎生成的投顧報告語言（llm_analyst.py）
* 圖表標題與座標軸標籤

---

## 📂 專案結構

    .
    ├── app.py               # Streamlit 主應用程式（三大分頁 UI、雙語介面與互動邏輯）
    ├── strategies.py        # 量化策略核心（數據抓取、MACD、夏普比率、組合分析、雙語訊號）
    ├── database.py          # SQLite 數據庫操作（持倉管理、交易歷史）
    ├── llm_analyst.py       # LLM 分析引擎（OpenAI 整合 + 啟發式 Fallback 規則引擎，支援雙語）
    ├── requirements.txt     # Python 依賴清單
    ├── trading_app.db       # SQLite 本地數據庫（首次運行自動生成，二進制檔案）
    └── README.md            # 專案完整設計架構與使用文件

---

## 📊 功能模組詳細說明

### A. 個股策略分析（strategies.py）

* 支援以完整或不完整的股票名稱、股票代號進行模糊搜尋，系統會從 Yahoo Finance 顯示最接近的股票結果供使用者選擇。

| 函式 | 功能描述 |
|------|----------|
| `fetch_stock_data(ticker, period)` | 透過 `yfinance` 抓取指定週期（6mo / 1y / 2y / 5y）的歷史股價 OHLCV 數據 |
| `fetch_fundamental_info(ticker)` | 抓取基本面資訊（Trailing P/E、Forward P/E、市值、貨幣、行業板塊等） |
| `calculate_macd(df)` | 計算 MACD 快線（EMA12 - EMA26）、訊號線（EMA9）及 Histogram 柱狀值 |
| `generate_signals(df, fundamental, language)` | 融合技術面與基本面，輸出加權交易信號與綜合結論（支援中文 / English 雙語文本） |
| `calculate_portfolio_metrics(...)` | 計算投資組合的年化收益率、波動率、夏普比率及個股對比指標 |

**信號判讀邏輯（四種綜合結論）：**
1. **強烈買入 (STRONG BUY)** — MACD 金叉 + P/E 處於合理偏低區間（動量與估值同步支持）
2. **投機性買入 (SPECULATIVE BUY)** — MACD 金叉但估值偏高（短線動能強，安全邊際不足）
3. **左側佈局 / 分注吸納 (ACCUMULATE)** — 估值低廉但技術面尚未轉強（低估值防守策略）
4. **建議減持 / 賣出 (SELL)** — MACD 死叉，技術指標轉弱

**P/E 估值分級標準：**
* P/E < 15 → 估值具吸引力（價值型標的）
* 15 ≤ P/E ≤ 30 → 合理成長範圍
* P/E > 30 → 估值偏高，留意成長預期兌現風險
* P/E 不可用或為負 → 可能處於虧損狀態

### B. 投資組合與夏普比率（Tab 2）

* 輸入多隻股票代號（以逗號分隔）及自訂權重，系統自動：
  1. 下載近一年歷史收盤價並計算每日收益率；
  2. 以 252 個交易日年化，計算組合預期年化回報率；
  3. 建構協方差矩陣，推導組合年化波動率；
  4. 計算夏普比率：(組合年化回報 − 無風險利率) / 組合波動率。
* 同時輸出**個股層面**的年化回報、波動率與夏普比率對比表，方便判斷哪隻股票拖累組合表現。
* 附帶**歷史累計淨值走勢圖**（基準點 = 1.0），直觀比較各資產表現。

> 💡 夏普比率參考標準：> 1 代表良好，> 2 代表優秀，負值代表表現遜於無風險利率。

### C. 持倉管理與交易日誌（database.py）

| 函式 | 功能描述 |
|------|----------|
| `init_db()` | 初始化數據庫，建立 `portfolio` 與 `trade_history` 兩張資料表 |
| `add_position(ticker, shares, cost_price)` | 新增持倉紀錄 |
| `get_portfolio()` | 以 DataFrame 形式讀取全部持倉 |
| `delete_position(position_id)` | 按 ID 刪除指定持倉 |
| `record_trade(ticker, action, shares, price, strategy_signal)` | 記錄模擬交易及其觸發的策略信號（供日後複盤） |
| `get_trade_history()` | 按時間倒序讀取完整交易歷史日誌 |

**數據庫架構：**

    -- 持倉表
    CREATE TABLE IF NOT EXISTS portfolio (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        shares REAL NOT NULL,
        cost_price REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    -- 交易歷史表
    CREATE TABLE IF NOT EXISTS trade_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ticker TEXT NOT NULL,
        action TEXT NOT NULL,          -- BUY (買入) / SELL (賣出)
        shares REAL NOT NULL,
        price REAL NOT NULL,
        strategy_signal TEXT,          -- 觸發當下的策略訊號 / 交易動機
        executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

### D. LLM 智能投顧報告（llm_analyst.py）

| 函式 | 功能描述 |
|------|----------|
| `generate_ai_analysis(ticker, signals, fundamental, openai_api_key, language)` | 呼叫 OpenAI API（gpt-3.5-turbo）生成專業白話分析報告（語言跟隨介面設定） |
| `fallback_heuristic_analysis(ticker, signals, fundamental, language)` | 無 API Key 時的啟發式規則引擎，基於量化信號生成香港語境解讀（支援雙語） |

**運作流程與防禦機制：**
1. 使用者可於側邊欄輸入自訂 OpenAI API Key（僅存於工作階段，不會寫入數據庫）。
2. 若 Key 格式有效（以 `sk-` 開頭）→ 呼叫 LLM 生成個人化深度分析。
3. 若無 Key 或格式不符 → 直接使用本地啟發式規則引擎，不發出任何網絡請求。
4. 若 API 異常（逾時 / 代理伺服器錯誤 / 無效 HTML 響應）→ 自動攔截並切換至 Fallback 引擎，確保報告永不中斷。
5. 內置 **4 秒硬性超時** 與 **零重試** 設定（`timeout=4.0`、`max_retries=0`），徹底防止連線掛起卡頓。
6. 報告語言自動跟隨側邊欄的介面語言設定（中文 / English）。

**報告內容架構（LLM 版）：**
1. 技術面與動能分析（解讀 MACD 訊號及背離狀況）
2. 基本面估值判斷（分析市盈率 P/E 是否合理）
3. 具體操作策略（買入、觀望或止蝕點位建議）
4. 針對個人投資者的風險提示

---

## 💡 建議使用流程

1. **個股診斷**：在「個股技術與估值策略」分頁輸入股票代號（如 `AAPL`、`MSFT`、`0700.HK`），選擇分析週期後執行 AI 診斷，查看 K 線圖、MACD 子圖及綜合信號。
2. **組合體檢**：在「投資組合分析」分頁輸入多隻持倉及權重，設定無風險利率，檢視夏普比率與累計淨值走勢，評估分散投資效果。
3. **記錄持倉**：在「倉位管理」分頁將實際持倉（股數、成本價）寫入 SQLite 數據庫，建立個人持倉清單。
4. **模擬交易複盤**：每次模擬買賣時記錄策略訊號與動機，日後透過交易歷史日誌檢視決策質素，培養投資紀律。
5. **善用 AI 報告**：有 API Key 時開啟 LLM 深度分析；無 Key 亦可靠啟發式引擎獲得基本解讀。
6. **雙語介面**：於側邊欄頂部「🌐 Language / 語言」一鍵切換中文 / English，所有分頁、訊號、報告與圖表文本即時同步切換。

---

## ⚠️ 免責聲明

本工具僅供教育及研究用途，所有輸出（包括 LLM 生成之分析報告）均不構成任何投資建議、要約或招攬。投資涉及風險，證券價格可升可跌，過往表現不代表將來表現。用戶應根據自身財務狀況及風險承受能力作出獨立判斷，必要時諮詢持牌專業人士。使用本系統所產生之任何損失，開發者概不負責。
