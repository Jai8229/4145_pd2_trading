import numpy as np
import pandas as pd
import yfinance as yf

def fetch_stock_data(ticker: str, period: str = "1y") -> pd.DataFrame:
    """下載指定股票的歷史數據"""
    stock = yf.Ticker(ticker)
    df = stock.history(period=period)
    if df.empty:
        raise ValueError(f"無法取得代號 {ticker} 的市場數據，請檢查股票代號。")
    return df

def fetch_fundamental_info(ticker: str) -> dict:
    """獲取基本面指標，如 P/E Ratio、Forward P/E 等"""
    stock = yf.Ticker(ticker)
    info = stock.info
    trailing_pe = info.get("trailingPE", None)
    forward_pe = info.get("forwardPE", None)
    market_cap = info.get("marketCap", None)
    currency = info.get("currency", "USD")
    company_name = info.get("shortName", ticker)
    sector = info.get("sector", "N/A")

    return {
        "ticker": ticker.upper(),
        "company_name": company_name,
        "sector": sector,
        "trailing_pe": trailing_pe,
        "forward_pe": forward_pe,
        "market_cap": market_cap,
        "currency": currency,
    }

def calculate_macd(df: pd.DataFrame, fast: int = 12, slow: int = 26, signal_span: int = 9) -> pd.DataFrame:
    """計算 MACD 線、訊號線及柱狀圖"""
    data = df.copy()
    data["EMA_fast"] = data["Close"].ewm(span=fast, adjust=False).mean()
    data["EMA_slow"] = data["Close"].ewm(span=slow, adjust=False).mean()
    data["MACD"] = data["EMA_fast"] - data["EMA_slow"]
    data["Signal_Line"] = data["MACD"].ewm(span=signal_span, adjust=False).mean()
    data["MACD_Hist"] = data["MACD"] - data["Signal_Line"]
    return data

def generate_signals(df: pd.DataFrame, fundamental: dict) -> dict:
    """結合 MACD 與 P/E ratio 評估綜合買賣信號"""
    data = calculate_macd(df)
    latest = data.iloc[-1]
    prev = data.iloc[-2]

    # MACD 技術面信號
    macd_signal = "持有 / 中性 (HOLD)"
    macd_reason = "MACD 指標處於平衡區間，無明顯交叉。"
    if prev["MACD"] < prev["Signal_Line"] and latest["MACD"] > latest["Signal_Line"]:
        macd_signal = "黃金交叉 (BUY)"
        macd_reason = "MACD 快線向上突破訊號線，短線動能顯著轉強。"
    elif prev["MACD"] > prev["Signal_Line"] and latest["MACD"] < latest["Signal_Line"]:
        macd_signal = "死亡交叉 (SELL)"
        macd_reason = "MACD 快線向下跌破訊號線，動能偏弱。"
    elif latest["MACD"] > latest["Signal_Line"]:
        macd_signal = "偏多 (BULLISH)"
        macd_reason = "MACD 維持於訊號線上方，多頭動能持續。"
    else:
        macd_signal = "偏空 (BEARISH)"
        macd_reason = "MACD 處於訊號線下方，空頭動能主導。"

    # P/E 基本面估值信號
    pe = fundamental.get("trailing_pe")
    pe_evaluation = "估值正常"
    pe_score = 0  # -1 代表過高，0 代表合理，1 代表低估
    if pe is None or pe <= 0:
        pe_evaluation = "市盈率不可用或為負數 (可能處於虧損狀態)"
        pe_score = -0.5
    elif pe < 15:
        pe_evaluation = f"市盈率 ({pe:.1f}x) 處於較低水平，估值具吸引力 (價值型標的)"
        pe_score = 1
    elif pe <= 30:
        pe_evaluation = f"市盈率 ({pe:.1f}x) 處於合理成長範圍"
        pe_score = 0.2
    else:
        pe_evaluation = f"市盈率 ({pe:.1f}x) 偏高，市場溢價較高，需留意成長預期兌現風險"
        pe_score = -1

    # 綜合決策
    final_verdict = "觀望 / 中性"
    action_color = "orange"
    if "BUY" in macd_signal and pe_score >= 0:
        final_verdict = "強烈買入 (STRONG BUY) - 動量與估值同步支持"
        action_color = "green"
    elif "BUY" in macd_signal and pe_score < 0:
        final_verdict = "投機性買入 (SPECULATIVE BUY) - 短線動能強，但估值偏高"
        action_color = "blue"
    elif "SELL" in macd_signal:
        final_verdict = "建議減持 / 賣出 (SELL) - 技術指標轉弱"
        action_color = "red"
    elif pe_score == 1 and "BEARISH" not in macd_signal:
        final_verdict = "左側佈局 / 分注吸納 (ACCUMULATE) - 低估值防守"
        action_color = "green"

    return {
        "macd_signal": macd_signal,
        "macd_reason": macd_reason,
        "pe_evaluation": pe_evaluation,
        "pe_score": pe_score,
        "final_verdict": final_verdict,
        "action_color": action_color,
        "latest_close": float(latest["Close"]),
        "latest_macd": float(latest["MACD"]),
        "latest_signal": float(latest["Signal_Line"]),
        "latest_hist": float(latest["MACD_Hist"]),
        "df_with_macd": data
    }

def calculate_portfolio_metrics(tickers: list[str], weights: list[float], period: str = "1y", risk_free_rate: float = 0.04) -> dict:
    """計算投資組合的預期年化回報率、波動率與夏普比率 (Sharpe Ratio)"""
    if not tickers or len(tickers) == 0:
        return {}

    # 下載歷史收盤價
    data = yf.download(tickers, period=period, progress=False)["Close"]
    if isinstance(data, pd.Series):
        data = data.to_frame()

    data = data.dropna()
    daily_returns = data.pct_change().dropna()

    w = np.array(weights)
    w = w / np.sum(w)  # 確保權重總和為 1

    # 預期年化收益率 (以 252 個交易日計算)
    mean_daily_return = daily_returns.mean()
    portfolio_annual_return = float(np.sum(mean_daily_return * w) * 252)

    # 協方差矩陣與年化波動率
    cov_matrix = daily_returns.cov() * 252
    portfolio_variance = float(np.dot(w.T, np.dot(cov_matrix, w)))
    portfolio_volatility = float(np.sqrt(portfolio_variance))

    # 夏普比率 (Sharpe Ratio) = (組合收益率 - 無風險利率) / 波動率
    if portfolio_volatility > 0:
        sharpe_ratio = float((portfolio_annual_return - risk_free_rate) / portfolio_volatility)
    else:
        sharpe_ratio = 0.0

    # 個股個別夏普比率
    individual_metrics = []
    for ticker in tickers:
        if ticker in daily_returns.columns:
            ret = float(daily_returns[ticker].mean() * 252)
            vol = float(daily_returns[ticker].std() * np.sqrt(252))
            sr = float((ret - risk_free_rate) / vol) if vol > 0 else 0.0
            individual_metrics.append({
                "ticker": ticker,
                "annual_return": ret,
                "volatility": vol,
                "sharpe_ratio": sr
            })

    return {
        "portfolio_return": portfolio_annual_return,
        "portfolio_volatility": portfolio_volatility,
        "sharpe_ratio": sharpe_ratio,
        "individual_metrics": individual_metrics,
        "daily_returns": daily_returns
    }
