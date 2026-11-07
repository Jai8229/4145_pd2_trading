import os
import openai

def generate_ai_analysis(ticker: str, signals: dict, fundamental: dict, openai_api_key: str = None) -> str:
    """使用 LLM 或內建模擬專家系統生成深度分析與投資決策報告"""
    
    prompt_context = f"""
股票代號: {ticker} ({fundamental.get('company_name', 'N/A')})
板塊: {fundamental.get('sector', 'N/A')}
最新收盤價: {signals['latest_close']:.2f} {fundamental.get('currency', 'USD')}
P/E (市盈率): {fundamental.get('trailing_pe')}
P/E 評估: {signals['pe_evaluation']}
MACD 現況: MACD={signals['latest_macd']:.3f}, Signal={signals['latest_signal']:.3f}, 柱狀圖={signals['latest_hist']:.3f}
MACD 趨勢判斷: {signals['macd_signal']} ({signals['macd_reason']})
系統綜合策略結論: {signals['final_verdict']}
"""

    if openai_api_key and openai_api_key.strip().startswith("sk-"):
        try:
            client = openai.OpenAI(api_key=openai_api_key)
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "你是一位在香港金融科技公司工作的資深特許金融分析師（CFA）。"
                            "你的任務是向非專業散戶投資者解釋這隻股票的策略訊號。"
                            "請使用繁體中文（香港慣用語法），包含：1. 技術面與動能分析（MACD 解讀）；"
                            "2. 基本面估值判斷（P/E Ratio 分析）；3. 具體操作策略（買入/觀望/止蝕位建議）；"
                            "4. 非專業投資者的風險提示。風格需客觀、清晰、具實操性。"
                        )
                    },
                    {
                        "role": "user",
                        "content": f"請分析以下數據並給出投資指導報告：\n{prompt_context}"
                    }
                ],
                temperature=0.7,
                max_tokens=700
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"⚠️ 呼叫 OpenAI API 發生錯誤 ({str(e)})，以下切換至內建金融 AI 顧問引擎：\n\n" + fallback_heuristic_analysis(ticker, signals, fundamental)

    return fallback_heuristic_analysis(ticker, signals, fundamental)

def fallback_heuristic_analysis(ticker: str, signals: dict, fundamental: dict) -> str:
    """內建金融 AI 分析引擎（即使沒有提供付費 API Key 亦能提供專業報告）"""
    pe_str = f"{fundamental.get('trailing_pe'):.1f}x" if fundamental.get('trailing_pe') else "暫無數據 / 負數"
    return f"""### 📊 AI 智能金融顧問投資報告 ({ticker})

#### 1. 技術動能評估 (MACD 指標)
* **當前狀態**：{signals['macd_signal']}
* **技術分析**：{signals['macd_reason']}。當前快線數值為 `{signals['latest_macd']:.3f}`，訊號線為 `{signals['latest_signal']:.3f}`，差離柱狀圖為 `{signals['latest_hist']:.3f}`。若柱狀圖由負翻正，往往暗示空頭力道竭盡；反之則代表回調壓力未消。

#### 2. 基本面與估值分析 (P/E Ratio)
* **當前歷史市盈率**：`{pe_str}`
* **估值解讀**：{signals['pe_evaluation']}。對於非專業投資者而言，不宜單憑 P/E 高低做決定；高 P/E 標的需具備高於行業平均的營收成長力，而超低 P/E 標的則需提防「價值陷阱」。

#### 3. 執行策略建議
* **綜合策略定調**：**{signals['final_verdict']}**
* **建議倉位管理**：
  - 若已持倉：建議將止蝕/止賺位設置於前波低點或移動平均支撐位，防止短線反轉。
  - 若未持倉：非專業投資者建議採取「金字塔式分批建倉」，切忌單次全倉追高。

#### 4. 散戶投資者專屬風險提示
* 股市受宏觀利率環境及公司財報波動影響，技術指標存在滯後性。建議結合個股所屬板塊整體走勢，並控制單隻股票在總投資組合中之佔比不超過 15% - 20%。
"""
