import os
import openai

def fallback_heuristic_analysis(ticker: str, signals: dict, fundamental: dict) -> str:
    """
    當無提供 API Key 或網絡請求失敗時的啟發式規則專家報告生成器
    """
    company_name = fundamental.get("company_name", ticker)
    pe = fundamental.get("trailing_pe")
    pe_eval = signals.get("pe_evaluation", "無數據")
    macd_sig = signals.get("macd_signal", "觀望")
    macd_reason = signals.get("macd_reason", "指標趨勢不明顯")
    final_verdict = signals.get("final_verdict", "觀望")
    latest_close = signals.get("latest_close", 0.0)
    currency = fundamental.get("currency", "USD")

    report = f"""### 📊 {ticker} ({company_name}) 專業量化策略分析報告 (專家規則引擎)

**現價**: {latest_close:.2f} {currency}  
**系統綜合建議**: **{final_verdict}**

---

#### 1. 技術面動能診斷 (MACD 指標)
- **最新狀態**: MACD 線: `{signals.get('latest_macd', 0):.3f}` | 信號線: `{signals.get('latest_signal', 0):.3f}` | 柱狀圖: `{signals.get('latest_hist', 0):.3f}`
- **訊號解讀**: **{macd_sig}**
- **動能分析**: {macd_reason}。當 MACD 柱狀圖持續擴大時，代表該方向動能強勁；若出現收斂則需提防趨勢反轉。

#### 2. 基本面估值判斷 (P/E Ratio)
- **滾動市盈率 (Trailing P/E)**: {f"{pe:.2f}" if pe else "N/A"}
- **估值評估**: **{pe_eval}**
- **價值分析**: 市盈率反映市場對該資產未來盈利增長的預期。過高可能存在估值透支風險，過低則可能受限於行業增長瓶頸或基本面隱憂。

#### 3. 具體操作策略與風險提示
- **建議操作**: 鑑於目前的綜合訊號為「**{final_verdict}**」，投資者宜審慎管理倉位。
- **止蝕/風控指引**: 若決定建倉，建議將止蝕位設定在近期波段低位（約現價下方 5% - 8% 區間），並避免於大市震盪時盲目追高。
- **風險提示**: 本報告由量化規則自動生成，僅供參考，不構成任何要約或投資決策保證。
"""
    return report

def generate_ai_analysis(ticker: str, signals: dict, fundamental: dict, openai_api_key: str = None) -> str:
    """
    調用 LLM 生成深度投資診斷，加入嚴格超時與代理錯誤防禦，確保絕不卡死
    """
    clean_key = str(openai_api_key).strip() if openai_api_key else ""
    # 若 API Key 未提供或格式不符，直接使用本地規則引擎，不發出任何網絡請求
    if not clean_key or not clean_key.startswith("sk-"):
        return fallback_heuristic_analysis(ticker, signals, fundamental)

    prompt_context = f"""
股票代號: {ticker} ({fundamental.get('company_name', 'N/A')})
板塊: {fundamental.get('sector', 'N/A')}
最新收盤價: {signals.get('latest_close', 0):.2f} {fundamental.get('currency', 'USD')}
P/E (市盈率): {fundamental.get('trailing_pe')}
P/E 評估: {signals.get('pe_evaluation')}
MACD 現況: MACD={signals.get('latest_macd', 0):.3f}, Signal={signals.get('latest_signal', 0):.3f}, 柱狀圖={signals.get('latest_hist', 0):.3f}
MACD 趨勢判斷: {signals.get('macd_signal')} ({signals.get('macd_reason')})
系統綜合策略結論: {signals.get('final_verdict')}
"""

    system_prompt = (
        "你是一位在香港金融機構工作的資深特許金融分析師（CFA）。"
        "你的任務是向投資者解釋這隻股票的策略訊號。"
        "請使用繁體中文（香港慣用語法），包含："
        "1. 技術面與動能分析（解讀 MACD 訊號及背離狀況）；"
        "2. 基本面估值判斷（分析市盈率 P/E 是否合理）；"
        "3. 具體操作策略（買入、觀望或止蝕點位建議）；"
        "4. 針對個人投資者的風險提示。"
        "風格需保持專業、客觀、清晰且具實操性。"
    )

    user_prompt = f"請根據以下量化數據生成一份投資診斷報告：\n{prompt_context}"

    try:
        # 若環境中存在 litellm 全域變量，設定保護防止背景無窮重試
        try:
            import litellm
            litellm.num_retries = 0
            litellm.request_timeout = 4.0
            litellm.drop_params = True
        except ImportError:
            pass

        # 檢測自訂代理 Base URL，若環境變量為無效路徑則退回標準 OpenAI 端點
        custom_base = os.environ.get("OPENAI_BASE_URL") or os.environ.get("OPENAI_API_BASE")
        if custom_base and not custom_base.rstrip("/").endswith("/v1"):
            custom_base = custom_base.rstrip("/") + "/v1"

        client_kwargs = {
            "api_key": clean_key,
            "timeout": 4.0,       # 4 秒硬性超時限制，防止連線掛起
            "max_retries": 0      # 嚴格禁止重試，防止反覆嘗試被阻擋的網絡端點
        }
        if custom_base:
            client_kwargs["base_url"] = custom_base

        client = openai.OpenAI(**client_kwargs)

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.3,
            max_tokens=700
        )
        content = response.choices[0].message.content
        if not content or "<!DOCTYPE html>" in content:
            raise ValueError("收到無效的 HTML 響應")
        return content

    except BaseException as e:
        # 完全攔截所有異常（包含 litellm.APIError / HTML 報錯 / 連線逾時），自動切換至專家規則引擎
        error_notice = f"（提示：AI 線上 API 連線受限 [{type(e).__name__}]，已自動切換至量化專家系統生成報告）\n\n"
        return error_notice + fallback_heuristic_analysis(ticker, signals, fundamental)
