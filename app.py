import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

import database
import strategies
import llm_analyst

st.set_page_config(
    page_title="AI 智投顧問 | FinTech Trading Pro",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化數據庫
database.init_db()

# 側邊欄設定
st.sidebar.title("⚙️ 控制面板與 API 設定")
st.sidebar.markdown("面向非專業投資者的全方位智能量化分析與組合管理系統。")

api_key = st.sidebar.text_input(
    "OpenAI API Key (選填)",
    type="password",
    help="提供 OpenAI API Key 可獲得由 GPT 生成的客製化深度投顧報告；若未提供將自動採用內建智能規則引擎。"
)

st.sidebar.divider()
st.sidebar.subheader("🌟 三大核心加強功能")
st.sidebar.markdown("""
1. **多股票投資組合與夏普比率 (Sharpe Ratio)**
2. **多維度策略 (MACD 動能 + P/E 估值分析)**
3. **LLM 智能投資顧問報告與 SQLite 本地倉位追蹤**
""")

# 頂部導航
tabs = st.tabs(["📊 個股技術與估值策略 (MACD + P/E)", "💼 投資組合分析與夏普比率 (Sharpe Ratio)", "🗄️ 倉位管理與模擬交易數據庫"])

# ==================== Tab 1: 個股策略 ====================
with tabs[0]:
    st.header("📈 單股多因子策略：MACD 技術動態與 P/E 估值結合")
    
    col_input1, col_input2, col_input3 = st.columns([2, 1, 1])
    with col_input1:
        selected_ticker = st.text_input("輸入股票代號 (支援美股/港股，如 AAPL, MSFT, 0700.HK):", value="AAPL").upper().strip()
    with col_input2:
        period_choice = st.selectbox("分析週期:", ["6mo", "1y", "2y", "5y"], index=1)
    with col_input3:
        run_analysis = st.button("執行 AI 診斷", use_container_width=True)

    if selected_ticker:
        try:
            with st.spinner(f"正在抓取 {selected_ticker} 實時行情與財務基本面數據..."):
                stock_data = strategies.fetch_stock_data(selected_ticker, period=period_choice)
                fundamental_info = strategies.fetch_fundamental_info(selected_ticker)
                signals = strategies.generate_signals(stock_data, fundamental_info)

            # 頂部指標卡片
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            latest_price = signals["latest_close"]
            kpi1.metric("公司名稱", fundamental_info.get("company_name", selected_ticker))
            kpi2.metric("最新收盤價", f"{latest_price:.2f} {fundamental_info.get('currency', 'USD')}")
            
            pe_val = fundamental_info.get("trailing_pe")
            kpi3.metric("歷史市盈率 (P/E)", f"{pe_val:.2f}x" if pe_val else "N/A")
            kpi4.metric("綜合策略訊號", signals["final_verdict"].split(" - ")[0])

            st.divider()

            # 互動式專業蠟燭圖 + MACD 子圖
            df_plot = signals["df_with_macd"]
            fig = make_subplots(
                rows=2, cols=1,
                shared_xaxes=True,
                vertical_spacing=0.08,
                subplot_titles=(f"{selected_ticker} K線圖與價格走勢", "MACD 指標 (快線 / 慢線 / 動能柱狀圖)"),
                row_width=[0.35, 0.65]
            )

            # 主圖：K線圖
            fig.add_trace(go.Candlestick(
                x=df_plot.index,
                open=df_plot['Open'],
                high=df_plot['High'],
                low=df_plot['Low'],
                close=df_plot['Close'],
                name="K線"
            ), row=1, col=1)

            # 子圖：MACD
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['MACD'], line=dict(color='blue', width=1.5), name="MACD (快線)"), row=2, col=1)
            fig.add_trace(go.Scatter(x=df_plot.index, y=df_plot['Signal_Line'], line=dict(color='orange', width=1.5), name="Signal (慢線)"), row=2, col=1)
            
            # 柱狀圖配色
            colors = np.where(df_plot['MACD_Hist'] < 0, 'crimson', 'forestgreen')
            fig.add_trace(go.Bar(x=df_plot.index, y=df_plot['MACD_Hist'], marker_color=colors, name="MACD Histogram"), row=2, col=1)

            fig.update_layout(height=650, xaxis_rangeslider_visible=False, template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)

            # 策略詳細評估與 LLM 報告
            c_left, c_right = st.columns([1, 1])
            with c_left:
                st.subheader("🎯 策略指標量化詳解")
                st.info(f"**MACD 狀態**：{signals['macd_signal']}\n\n**分析詳情**：{signals['macd_reason']}")
                st.warning(f"**P/E 估值分位**：\n\n{signals['pe_evaluation']}")
                st.success(f"**綜合決策結論**：\n\n{signals['final_verdict']}")

            with c_right:
                st.subheader("🤖 LLM 智能投資顧問報告")
                ai_report = llm_analyst.generate_ai_analysis(selected_ticker, signals, fundamental_info, openai_api_key=api_key)
                st.markdown(ai_report)

        except Exception as err:
            st.error(f"分析時發生錯誤: {err}")

# ==================== Tab 2: 投資組合與夏普比率 ====================
with tabs[1]:
    st.header("💼 投資組合分析 (Portfolio Analytics & Sharpe Ratio)")
    st.markdown("""
    分散投資是降低非系統性風險的核心途徑。此處計算多股票投資組合的**預期回報率**、**年化波動率**，以及衡量性價比的**夏普比率 (Sharpe Ratio)**。
    """)

    col_pf1, col_pf2 = st.columns([2, 1])
    with col_pf1:
        default_tickers = "AAPL, MSFT, GOOGL, NVDA"
        user_tickers_str = st.text_input("輸入投資組合股票清單 (以逗號分隔):", value=default_tickers)
    with col_pf2:
        rf_rate = st.number_input("基準無風險利率 (例如美國國債收益率 4%):", min_value=0.0, max_value=0.15, value=0.04, step=0.005)

    tickers_list = [t.strip().upper() for t in user_tickers_str.split(",") if t.strip()]

    if len(tickers_list) < 2:
        st.warning("請至少輸入 2 隻或以上之股票代號進行多資產組合分析。")
    else:
        st.subheader("資產權重配置 (%)")
        cols = st.columns(len(tickers_list))
        weights = []
        equal_weight = round(100.0 / len(tickers_list), 1)
        for idx, ticker in enumerate(tickers_list):
            with cols[idx]:
                w = st.number_input(f"{ticker} 權重", min_value=0.0, max_value=100.0, value=equal_weight, step=1.0, key=f"w_{ticker}")
                weights.append(w)

        if sum(weights) == 0:
            st.error("權重總和不能為 0。")
        else:
            try:
                with st.spinner("正在下載投資組合歷史時序數據並計算協方差矩陣..."):
                    pf_results = strategies.calculate_portfolio_metrics(tickers_list, weights, period="1y", risk_free_rate=rf_rate)

                p1, p2, p3 = st.columns(3)
                p1.metric("組合預期年化回報率", f"{pf_results['portfolio_return']*100:.2f}%")
                p2.metric("組合年化波動率 (標準差)", f"{pf_results['portfolio_volatility']*100:.2f}%")
                
                sr = pf_results['sharpe_ratio']
                sr_color = "normal" if sr >= 1 else "off"
                p3.metric("投資組合夏普比率 (Sharpe Ratio)", f"{sr:.2f}", help="Sharpe > 1 代表良好，> 2 代表優秀，負值代表表現遜於無風險利率。")

                st.divider()

                # 個股夏普比率與表現對比表格
                st.subheader("個股與組合夏普比率效益對比")
                ind_df = pd.DataFrame(pf_results['individual_metrics'])
                ind_df.columns = ["股票代號", "年化回報率", "年化波動率", "夏普比率 (Sharpe)"]
                ind_df["年化回報率"] = ind_df["年化回報率"].apply(lambda x: f"{x*100:.2f}%")
                ind_df["年化波動率"] = ind_df["年化波動率"].apply(lambda x: f"{x*100:.2f}%")
                ind_df["夏普比率 (Sharpe)"] = ind_df["夏普比率 (Sharpe)"].apply(lambda x: f"{x:.2f}")

                st.dataframe(ind_df, use_container_width=True)

                # 累計收益率曲線圖
                st.subheader("資產歷史走勢對比 (Normalized Cumulative Returns)")
                daily_ret = pf_results["daily_returns"]
                cum_returns = (1 + daily_ret).cumprod()

                fig_cum = go.Figure()
                for col in cum_returns.columns:
                    fig_cum.add_trace(go.Scatter(x=cum_returns.index, y=cum_returns[col], name=col))
                
                fig_cum.update_layout(
                    title="歷史累積淨值走勢 (基準點 = 1.0)",
                    xaxis_title="日期",
                    yaxis_title="累計淨值倍數",
                    template="plotly_white",
                    height=450
                )
                st.plotly_chart(fig_cum, use_container_width=True)

            except Exception as e:
                st.error(f"計算投資組合指標時發生錯誤: {e}")

# ==================== Tab 3: SQLite 數據庫持倉管理 ====================
with tabs[2]:
    st.header("🗄️ 投資組合管理與模擬交易日誌 (SQLite 數據庫驅動)")
    st.markdown("所有持倉數據均保存在本地 SQLite 數據庫中，讓非專業投資者能夠系統化記錄買入成本與策略理由。")

    subcol1, subcol2 = st.columns([1, 1])

    with subcol1:
        st.subheader("新增持倉紀錄")
        with st.form("add_position_form"):
            new_ticker = st.text_input("股票代號 (Ticker):", value="AAPL").upper().strip()
            new_shares = st.number_input("持有股數 (Shares):", min_value=0.01, value=10.0, step=1.0)
            new_cost = st.number_input("平均成本價 (Cost Price):", min_value=0.01, value=180.0, step=0.5)
            submit_pos = st.form_submit_button("寫入數據庫")

            if submit_pos:
                database.add_position(new_ticker, new_shares, new_cost)
                st.success(f"成功將 {new_shares} 股 {new_ticker} (成本: {new_cost}) 加入數據庫！")

    with subcol2:
        st.subheader("執行策略模擬交易並記錄日誌")
        with st.form("trade_form"):
            trade_ticker = st.text_input("交易標的:", value="AAPL").upper().strip()
            trade_action = st.selectbox("動作:", ["BUY (買入)", "SELL (賣出)"])
            trade_shares = st.number_input("交易股數:", min_value=0.01, value=5.0, step=1.0)
            trade_price = st.number_input("執行價格:", min_value=0.01, value=185.0, step=0.5)
            trade_reason = st.text_input("策略訊號/交易動機:", value="MACD 金叉觸發買入")
            submit_trade = st.form_submit_button("記錄交易日誌")

            if submit_trade:
                database.record_trade(trade_ticker, trade_action, trade_shares, trade_price, trade_reason)
                st.success("交易記錄已成功寫入交易日誌資料庫！")

    st.divider()

    col_view1, col_view2 = st.columns([1, 1])
    with col_view1:
        st.subheader("現有持倉清單")
        pos_df = database.get_portfolio()
        if pos_df.empty:
            st.info("目前數據庫內暫無持倉資料，請於上方新增。")
        else:
            st.dataframe(pos_df, use_container_width=True)
            delete_id = st.number_input("輸入欲刪除的持倉 ID:", min_value=1, step=1)
            if st.button("刪除指定持倉"):
                database.delete_position(int(delete_id))
                st.warning(f"已從數據庫中刪除 ID: {delete_id}")
                st.rerun()

    with col_view2:
        st.subheader("歷史模擬交易日誌")
        trades_df = database.get_trade_history()
        if trades_df.empty:
            st.info("尚無交易記錄。")
        else:
            st.dataframe(trades_df, use_container_width=True)
