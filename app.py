import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

import database
import strategies
import llm_analyst

# ==================== 語言切換 (Language Switching) ====================
if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"

st.set_page_config(
    page_title=("AI Investment Advisor | FinTech Trading Pro" if st.session_state["lang"] == "en" else "AI 智投顧問 | FinTech Trading Pro"),
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 側邊欄頂部語言切換按鈕
lang_choice = st.sidebar.radio(
    "🌐 Language / 語言",
    options=["中文 (繁體)", "English"],
    horizontal=True,
)
LANG = "zh" if lang_choice == "中文 (繁體)" else "en"
st.session_state["lang"] = LANG

# ==================== 多語言文本字典 (UI Text i18n) ====================
TRANSLATIONS = {
    "zh": {
        "app_title": "⚙️ 控制面板與 API 設定",
        "app_subtitle": "面向非專業投資者的全方位智能量化分析與組合管理系統。",
        "api_key_label": "OpenAI API Key (選填)",
        "api_key_help": "提供 OpenAI API Key 可獲得由 GPT 生成的客製化深度投顧報告；若未提供將自動採用內建智能規則引擎。",
        "features_title": "🌟 三大核心加強功能",
        "features_body": "1. **多股票投資組合與夏普比率 (Sharpe Ratio)**\n2. **多維度策略 (MACD 動能 + P/E 估值分析)**\n3. **LLM 智能投資顧問報告與 SQLite 本地倉位追蹤**",
        "tab1": "📊 個股技術與估值策略 (MACD + P/E)",
        "tab2": "💼 投資組合分析與夏普比率 (Sharpe Ratio)",
        "tab3": "🗄️ 倉位管理與模擬交易數據庫",
        "tab1_header": "📈 單股多因子策略：MACD 技術動態與 P/E 估值結合",
        "ticker_label": "輸入股票代號或公司名稱 (支援模糊搜尋，如 AAPL、Apple、0700.HK):",
        "stock_match_label": "選擇最接近的股票:",
        "stock_match_help": "可輸入不完整的股票名稱或代號，系統會從 Yahoo Finance 顯示最接近的結果。",
        "period_label": "分析週期:",
        "run_button": "執行 AI 診斷",
        "fetching_spinner": "正在抓取 {ticker} 實時行情與財務基本面數據...",
        "kpi_company": "公司名稱",
        "kpi_close": "最新收盤價",
        "kpi_pe": "歷史市盈率 (P/E)",
        "kpi_signal": "綜合策略訊號",
        "chart_price_title": "{ticker} K線圖與價格走勢",
        "chart_macd_title": "MACD 指標 (快線 / 慢線 / 動能柱狀圖)",
        "trace_candle": "K線",
        "trace_macd": "MACD (快線)",
        "trace_signal": "Signal (慢線)",
        "trace_hist": "MACD Histogram",
        "strategy_detail_header": "🎯 策略指標量化詳解",
        "llm_report_header": "🤖 LLM 智能投資顧問報告",
        "macd_status_label": "**MACD 狀態**：{sig}\n\n**分析詳情**：{reason}",
        "pe_eval_label": "**P/E 估值分位**：\n\n{eval}",
        "verdict_label": "**綜合決策結論**：\n\n{verdict}",
        "tab1_error": "分析時發生錯誤: {err}",
        "tab2_header": "💼 投資組合分析 (Portfolio Analytics & Sharpe Ratio)",
        "tab2_desc": "分散投資是降低非系統性風險的核心途徑。此處計算多股票投資組合的**預期回報率**、**年化波動率**，以及衡量性價比的**夏普比率 (Sharpe Ratio)**。",
        "tickers_label": "輸入投資組合股票清單 (以逗號分隔):",
        "rf_label": "基準無風險利率 (例如美國國債收益率 4%):",
        "min_two_warning": "請至少輸入 2 隻或以上之股票代號進行多資產組合分析。",
        "weights_header": "資產權重配置 (%)",
        "weight_label": "{ticker} 權重",
        "zero_weight_error": "權重總和不能為 0。",
        "pf_spinner": "正在下載投資組合歷史時序數據並計算協方差矩陣...",
        "kpi_pf_return": "組合預期年化回報率",
        "kpi_pf_vol": "組合年化波動率 (標準差)",
        "kpi_pf_sharpe": "投資組合夏普比率 (Sharpe Ratio)",
        "sharpe_help": "Sharpe > 1 代表良好，> 2 代表優秀，負值代表表現遜於無風險利率。",
        "ind_table_header": "個股與組合夏普比率效益對比",
        "col_ticker": "股票代號",
        "col_return": "年化回報率",
        "col_vol": "年化波動率",
        "col_sharpe": "夏普比率 (Sharpe)",
        "cum_header": "資產歷史走勢對比 (Normalized Cumulative Returns)",
        "cum_chart_title": "歷史累積淨值走勢 (基準點 = 1.0)",
        "xaxis_date": "日期",
        "yaxis_nav": "累計淨值倍數",
        "pf_error": "計算投資組合指標時發生錯誤: {err}",
        "tab3_header": "🗄️ 投資組合管理與模擬交易日誌 (SQLite 數據庫驅動)",
        "tab3_desc": "所有持倉數據均保存在本地 SQLite 數據庫中，讓非專業投資者能夠系統化記錄買入成本與策略理由。",
        "add_pos_header": "新增持倉紀錄",
        "pos_ticker_label": "股票代號 (Ticker):",
        "pos_shares_label": "持有股數 (Shares):",
        "pos_cost_label": "平均成本價 (Cost Price):",
        "pos_submit": "寫入數據庫",
        "pos_success": "成功將 {shares} 股 {ticker} (成本: {cost}) 加入數據庫！",
        "trade_header": "執行策略模擬交易並記錄日誌",
        "trade_ticker_label": "交易標的:",
        "trade_action_label": "動作:",
        "action_buy": "BUY (買入)",
        "action_sell": "SELL (賣出)",
        "trade_shares_label": "交易股數:",
        "trade_price_label": "執行價格:",
        "trade_reason_label": "策略訊號/交易動機:",
        "trade_reason_default": "MACD 金叉觸發買入",
        "trade_submit": "記錄交易日誌",
        "trade_success": "交易記錄已成功寫入交易日誌資料庫！",
        "positions_header": "現有持倉清單",
        "no_positions": "目前數據庫內暫無持倉資料，請於上方新增。",
        "delete_id_label": "輸入欲刪除的持倉 ID:",
        "delete_button": "刪除指定持倉",
        "delete_success": "已從數據庫中刪除 ID: {id}",
        "trades_header": "歷史模擬交易日誌",
        "no_trades": "尚無交易記錄。",
    },
    "en": {
        "app_title": "⚙️ Control Panel & API Settings",
        "app_subtitle": "An all-in-one intelligent quantitative analysis and portfolio management system for non-professional investors.",
        "api_key_label": "OpenAI API Key (Optional)",
        "api_key_help": "Provide your OpenAI API Key to get a customised in-depth advisor report generated by GPT; if omitted, the built-in smart rule engine will be used automatically.",
        "features_title": "🌟 Three Core Enhanced Features",
        "features_body": "1. **Multi-stock portfolio & Sharpe Ratio**\n2. **Multi-factor strategy (MACD momentum + P/E valuation)**\n3. **LLM investment advisor report & local SQLite position tracking**",
        "tab1": "📊 Stock Technical & Valuation Strategy (MACD + P/E)",
        "tab2": "💼 Portfolio Analytics & Sharpe Ratio",
        "tab3": "🗄️ Position Management & Simulated Trading Database",
        "tab1_header": "📈 Single-Stock Multi-Factor Strategy: MACD Momentum + P/E Valuation",
        "ticker_label": "Enter a ticker or company name (fuzzy search, e.g. AAPL, Apple, 0700.HK):",
        "stock_match_label": "Choose the closest stock match:",
        "stock_match_help": "Enter a partial company name or ticker and choose the closest Yahoo Finance result.",
        "period_label": "Analysis period:",
        "run_button": "Run AI Diagnosis",
        "fetching_spinner": "Fetching real-time market data and fundamentals for {ticker}...",
        "kpi_company": "Company",
        "kpi_close": "Latest Close",
        "kpi_pe": "Trailing P/E",
        "kpi_signal": "Overall Signal",
        "chart_price_title": "{ticker} Candlestick & Price Trend",
        "chart_macd_title": "MACD Indicator (Fast / Slow / Histogram)",
        "trace_candle": "Candlestick",
        "trace_macd": "MACD (Fast)",
        "trace_signal": "Signal (Slow)",
        "trace_hist": "MACD Histogram",
        "strategy_detail_header": "🎯 Quantitative Strategy Breakdown",
        "llm_report_header": "🤖 LLM Investment Advisor Report",
        "macd_status_label": "**MACD Status**: {sig}\n\n**Details**: {reason}",
        "pe_eval_label": "**P/E Valuation**: \n\n{eval}",
        "verdict_label": "**Overall Verdict**: \n\n{verdict}",
        "tab1_error": "Error during analysis: {err}",
        "tab2_header": "💼 Portfolio Analytics & Sharpe Ratio",
        "tab2_desc": "Diversification is a core way to reduce unsystematic risk. This section computes the portfolio's **expected return**, **annualised volatility**, and the **Sharpe Ratio** as a risk-adjusted performance measure.",
        "tickers_label": "Enter portfolio tickers (comma-separated):",
        "rf_label": "Risk-free rate (e.g. US Treasury yield 4%):",
        "min_two_warning": "Please enter at least 2 tickers for multi-asset portfolio analysis.",
        "weights_header": "Asset Weight Allocation (%)",
        "weight_label": "{ticker} Weight",
        "zero_weight_error": "Total weight cannot be 0.",
        "pf_spinner": "Downloading portfolio historical data and computing the covariance matrix...",
        "kpi_pf_return": "Portfolio Expected Annual Return",
        "kpi_pf_vol": "Portfolio Annual Volatility (Std Dev)",
        "kpi_pf_sharpe": "Portfolio Sharpe Ratio",
        "sharpe_help": "Sharpe > 1 is good, > 2 is excellent; a negative value means the portfolio underperforms the risk-free rate.",
        "ind_table_header": "Individual vs Portfolio Sharpe Ratio Comparison",
        "col_ticker": "Ticker",
        "col_return": "Annual Return",
        "col_vol": "Annual Volatility",
        "col_sharpe": "Sharpe Ratio",
        "cum_header": "Asset Historical Performance (Normalized Cumulative Returns)",
        "cum_chart_title": "Cumulative NAV Trend (Base = 1.0)",
        "xaxis_date": "Date",
        "yaxis_nav": "Cumulative NAV Multiple",
        "pf_error": "Error calculating portfolio metrics: {err}",
        "tab3_header": "🗄️ Portfolio Management & Simulated Trading Log (SQLite Powered)",
        "tab3_desc": "All position data is stored in a local SQLite database, allowing non-professional investors to systematically record cost basis and strategy rationale.",
        "add_pos_header": "Add New Position",
        "pos_ticker_label": "Ticker:",
        "pos_shares_label": "Shares held:",
        "pos_cost_label": "Average cost price:",
        "pos_submit": "Save to Database",
        "pos_success": "Successfully added {shares} shares of {ticker} (cost: {cost}) to the database!",
        "trade_header": "Execute Simulated Trade & Log It",
        "trade_ticker_label": "Trade ticker:",
        "trade_action_label": "Action:",
        "action_buy": "BUY",
        "action_sell": "SELL",
        "trade_shares_label": "Trade shares:",
        "trade_price_label": "Execution price:",
        "trade_reason_label": "Strategy signal / trade rationale:",
        "trade_reason_default": "MACD golden cross triggered buy",
        "trade_submit": "Log Trade",
        "trade_success": "Trade record successfully written to the trade log database!",
        "positions_header": "Current Positions",
        "no_positions": "No positions in the database yet. Please add one above.",
        "delete_id_label": "Enter the position ID to delete:",
        "delete_button": "Delete Position",
        "delete_success": "Deleted ID {id} from the database",
        "trades_header": "Historical Simulated Trade Log",
        "no_trades": "No trade records yet.",
    },
}

def t(key: str) -> str:
    """依目前介面語言取得對應文本"""
    return TRANSLATIONS[LANG].get(key, TRANSLATIONS["zh"].get(key, key))

# 初始化數據庫
database.init_db()

# 側邊欄設定
st.sidebar.title(t("app_title"))
st.sidebar.markdown(t("app_subtitle"))

api_key = st.sidebar.text_input(
    t("api_key_label"),
    type="password",
    help=t("api_key_help")
)

st.sidebar.divider()
st.sidebar.subheader(t("features_title"))
st.sidebar.markdown(t("features_body"))

# 頂部導航
tabs = st.tabs([t("tab1"), t("tab2"), t("tab3")])

# ==================== Tab 1: 個股策略 ====================
with tabs[0]:
    st.header(t("tab1_header"))
    
    col_input1, col_input2, col_input3 = st.columns([2, 1, 1])
    with col_input1:
        stock_query = st.text_input(t("ticker_label"), value="AAPL").strip()
    with col_input2:
        period_choice = st.selectbox(t("period_label"), ["6mo", "1y", "2y", "5y"], index=1)
    with col_input3:
        run_analysis = st.button(t("run_button"), use_container_width=True)

    selected_ticker = stock_query.upper()
    if stock_query:
        candidates = strategies.search_stock_candidates(stock_query)
        if candidates and candidates[0]["symbol"] != selected_ticker:
            candidate_options = [
                f'{candidate["symbol"]} — {candidate["name"]}'
                for candidate in candidates
            ]
            selected_option = st.selectbox(
                t("stock_match_label"),
                candidate_options,
                help=t("stock_match_help"),
            )
            selected_ticker = selected_option.split(" — ", 1)[0]

        try:
            with st.spinner(t("fetching_spinner").format(ticker=selected_ticker)):
                stock_data = strategies.fetch_stock_data(selected_ticker, period=period_choice)
                fundamental_info = strategies.fetch_fundamental_info(selected_ticker)
                signals = strategies.generate_signals(stock_data, fundamental_info, language=LANG)

            # 頂部指標卡片
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            latest_price = signals["latest_close"]
            kpi1.metric(t("kpi_company"), fundamental_info.get("company_name", selected_ticker))
            kpi2.metric(t("kpi_close"), f"{latest_price:.2f} {fundamental_info.get('currency', 'USD')}")
            
            pe_val = fundamental_info.get("trailing_pe")
            kpi3.metric(t("kpi_pe"), f"{pe_val:.2f}x" if pe_val else "N/A")
            kpi4.metric(t("kpi_signal"), signals["final_verdict"].split(" - ")[0])

            st.divider()

            # 互動式專業蠟燭圖 + MACD 子圖
            df_plot = signals["df_with_macd"]
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                subplot_titles=(t("chart_price_title").format(ticker=selected_ticker), t("chart_macd_title")),
                row_width=[0.35, 0.65]
            )

            # 主圖：K線圖
            fig.add_trace(go.Candlestick(
                x=df_plot.index,
                open=df_plot['Open'],
                high=df_plot['High'],
                low=df_plot['Low'],
                close=df_plot['Close'],
                name=t("trace_candle")
            ), row=1, col=1)

            # 子圖：MACD
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD'], line=dict(color='blue', width=1.5), name=t("trace_macd")), row=2, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Signal_Line'], line=dict(color='orange', width=1.5), name=t("trace_signal")), row=2, col=1)
            
            # 柱狀圖配色
            colors = np.where(df_plot['MACD_Hist'] < 0, 'crimson', 'forestgreen')
            fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['MACD_Hist'], marker_color=colors, name=t("trace_hist")), row=2, col=1)

            fig.update_layout(height=650, xaxis_rangeslider_visible=False, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # 策略詳細評估與 LLM 報告
            c_left, c_right = st.columns([1, 1])
            with c_left:
                st.subheader(t("strategy_detail_header"))
                st.info(t("macd_status_label").format(sig=signals['macd_signal'], reason=signals['macd_reason']))
                st.warning(t("pe_eval_label").format(eval=signals['pe_evaluation']))
                st.success(t("verdict_label").format(verdict=signals['final_verdict']))

            with c_right:
                st.subheader(t("llm_report_header"))
                ai_report = llm_analyst.generate_ai_analysis(selected_ticker, signals, fundamental_info, openai_api_key=api_key, language=LANG)
                st.markdown(ai_report)

        except Exception as err:
            st.error(t("tab1_error").format(err=err))

# ==================== Tab 2: 投資組合與夏普比率 ====================
with tabs[1]:
    st.header(t("tab2_header"))
    st.markdown(t("tab2_desc"))

    col_pf1, col_pf2 = st.columns([2, 1])
    with col_pf1:
        default_tickers = "AAPL, MSFT, GOOGL, NVDA"
        user_tickers_str = st.text_input(t("tickers_label"), value=default_tickers)
    with col_pf2:
        rf_rate = st.number_input(t("rf_label"), min_value=0.0, max_value=0.15, value=0.04, step=0.005)

    tickers_list = [tk.strip().upper() for tk in user_tickers_str.split(",") if tk.strip()]

    if len(tickers_list) < 2:
        st.warning(t("min_two_warning"))
    else:
        st.subheader(t("weights_header"))
        cols = st.columns(len(tickers_list))
        weights = []
        equal_weight = round(100.0 / len(tickers_list), 1)
        for idx, ticker in enumerate(tickers_list):
            with cols[idx]:
                w = st.number_input(t("weight_label").format(ticker=ticker), min_value=0.0, max_value=100.0, value=equal_weight, step=1.0, key=f"w_{ticker}")
                weights.append(w)

        if sum(weights) == 0:
            st.error(t("zero_weight_error"))
        else:
            try:
                with st.spinner(t("pf_spinner")):
                    pf_results = strategies.calculate_portfolio_metrics(tickers_list, weights, period="1y", risk_free_rate=rf_rate)

                p1, p2, p3 = st.columns(3)
                p1.metric(t("kpi_pf_return"), f"{pf_results['portfolio_return']*100:.2f}%")
                p2.metric(t("kpi_pf_vol"), f"{pf_results['portfolio_volatility']*100:.2f}%")
                
                sr = pf_results['sharpe_ratio']
                p3.metric(t("kpi_pf_sharpe"), f"{sr:.2f}", help=t("sharpe_help"))

                st.divider()

                # 個股夏普比率與表現對比表格
                st.subheader(t("ind_table_header"))
                ind_df = pd.DataFrame(pf_results['individual_metrics'])
                ind_df.columns = [t("col_ticker"), t("col_return"), t("col_vol"), t("col_sharpe")]
                ind_df[t("col_return")] = ind_df[t("col_return")].apply(lambda x: f"{x*100:.2f}%")
                ind_df[t("col_vol")] = ind_df[t("col_vol")].apply(lambda x: f"{x*100:.2f}%")
                ind_df[t("col_sharpe")] = ind_df[t("col_sharpe")].apply(lambda x: f"{x:.2f}")

                st.dataframe(ind_df, use_container_width=True)

                # 累計收益率曲線圖
                st.subheader(t("cum_header"))
                daily_ret = pf_results["daily_returns"]
                cum_returns = (1 + daily_ret).cumprod()

                fig_cum = go.Figure()
                for col in cum_returns.columns:
                    fig_cum.add_trace(go.Scatter(x=cum_returns.index, y=cum_returns[col], name=col))
                
                fig_cum.update_layout(
                    title=t("cum_chart_title"),
                    xaxis_title=t("xaxis_date"),
                    yaxis_title=t("yaxis_nav"),
                    template="plotly_white",
                    height=450
                )
                st.plotly_chart(fig_cum, use_container_width=True)

            except Exception as e:
                st.error(t("pf_error").format(err=e))

# ==================== Tab 3: SQLite 數據庫持倉管理 ====================
with tabs[2]:
    st.header(t("tab3_header"))
    st.markdown(t("tab3_desc"))

    subcol1, subcol2 = st.columns([1, 1])

    with subcol1:
        st.subheader(t("add_pos_header"))
        with st.form("add_position_form"):
            new_ticker = st.text_input(t("pos_ticker_label"), value="AAPL").upper().strip()
            new_shares = st.number_input(t("pos_shares_label"), min_value=0.01, value=10.0, step=1.0)
            new_cost = st.number_input(t("pos_cost_label"), min_value=0.01, value=180.0, step=0.5)
            submit_pos = st.form_submit_button(t("pos_submit"))

            if submit_pos:
                database.add_position(new_ticker, new_shares, new_cost)
                st.success(t("pos_success").format(shares=new_shares, ticker=new_ticker, cost=new_cost))

    with subcol2:
        st.subheader(t("trade_header"))
        with st.form("trade_form"):
            trade_ticker = st.text_input(t("trade_ticker_label"), value="AAPL").upper().strip()
            trade_action = st.selectbox(t("trade_action_label"), [t("action_buy"), t("action_sell")])
            trade_shares = st.number_input(t("trade_shares_label"), min_value=0.01, value=5.0, step=1.0)
            trade_price = st.number_input(t("trade_price_label"), min_value=0.01, value=185.0, step=0.5)
            trade_reason = st.text_input(t("trade_reason_label"), value=t("trade_reason_default"))
            submit_trade = st.form_submit_button(t("trade_submit"))

            if submit_trade:
                database.record_trade(trade_ticker, trade_action, trade_shares, trade_price, trade_reason)
                st.success(t("trade_success"))

    st.divider()

    col_view1, col_view2 = st.columns([1, 1])
    with col_view1:
        st.subheader(t("positions_header"))
        pos_df = database.get_portfolio()
        if pos_df.empty:
            st.info(t("no_positions"))
        else:
            st.dataframe(pos_df, use_container_width=True)
            delete_id = st.number_input(t("delete_id_label"), min_value=1, step=1)
            if st.button(t("delete_button")):
                database.delete_position(int(delete_id))
                st.warning(t("delete_success").format(id=delete_id))
                st.rerun()

    with col_view2:
        st.subheader(t("trades_header"))
        trades_df = database.get_trade_history()
        if trades_df.empty:
            st.info(t("no_trades"))
        else:
            st.dataframe(trades_df, use_container_width=True)
