# `fetch_15y_data.py` & `HIST_DATA.csv` — Column Definitions (Exact 40-Column Order)

> **Script Path:** [`C:\Users\vinay\.gemini\Fyers_Hist\Fyers\fetch_15y_data.py`](file:///C:/Users/vinay/.gemini/Fyers_Hist/Fyers/fetch_15y_data.py)  
> **Output Dataset:** `HIST_DATA.csv` (Sorted by `DATETIME` Descending per Symbol)

---

## Exact Column Sequence (1 to 40)

| # | Column Name | Formula / Logic | Description |
|---|---|---|---|
| 1 | **`SYMBOL`** | String identifier | Index ticker symbol (e.g., `NSE:NIFTY50-INDEX`). |
| 2 | **`DATETIME`** | `DD-MMM-YYYY` | Trading date (**Sorted Descending** per symbol). |
| 3 | **`OPEN`** | Price | Opening price of the session. |
| 4 | **`HIGH`** | Price | Highest price reached during the session. |
| 5 | **`LOW`** | Price | Lowest price reached during the session. |
| 6 | **`CLOSE`** | Price | Closing price of the session. |
| 7 | **`CHANGE`** | `CLOSE - PREVIOUS_CLOSE` | Net point change from previous close. |
| 8 | **`CHANGE_PERCENT`** | `(CHANGE / PREVIOUS_CLOSE) * 100` | Net percentage return of the session. |
| 9 | **`TOTAL_LOW_HIGH`** | `HIGH - LOW` | Total daily high-to-low range in points. |
| 10 | **`GAP`** | `'gap up'` / `'gap down'` / `'no gap'` | Opening gap classification relative to previous close. |
| 11 | **`GAP_PERCENT`** | `((OPEN - PREVIOUS_CLOSE) / PREVIOUS_CLOSE) * 100` | Opening gap percentage magnitude. |
| 12 | **`TOTAL_PREV_LOW_HIGH`** | • Up Day: `HIGH_today - LOW_prev` <br> • Down Day: `HIGH_prev - LOW_today` | Directional 2-day move span in points. |
| 13 | **`TOTAL_PREV_LOW_HIGH_PERCENT`** | `(TOTAL_PREV_LOW_HIGH / PREVIOUS_CLOSE) * 100` | Percentage 2-day directional move span. |
| 14 | **`UPPER_WICK`** | `HIGH - max(OPEN, CLOSE)` | Size of upper candle wick in points. |
| 15 | **`LOWER_WICK`** | `min(OPEN, CLOSE) - LOW` | Size of lower candle wick in points. |
| 16 | **`VOLUME`** | Traded Volume | Total volume traded (0 if not available). |
| 17 | **`LOW_CLOSE`** | `CLOSE - LOW` | Points distance between Low and Close. |
| 18 | **`HIGH_CLOSE`** | `CLOSE - HIGH` | Points distance between Close and High. |
| 19 | **`PREVIOUS_CLOSE`** | `CLOSE.shift(1)` | Closing price of the previous trading day. |
| 20 | **`HIGH_52W`** | `HIGH.rolling(252).max()` | 52-week rolling maximum high. |
| 21 | **`LOW_52W`** | `LOW.rolling(252).min()` | 52-week rolling minimum low. |
| 22 | **`DIST_HIGH52`** | `((CLOSE - HIGH_52W) / HIGH_52W) * 100` | Percentage distance from 52-week High. |
| 23 | **`DIST_LOW52`** | `((CLOSE - LOW_52W) / LOW_52W) * 100` | Percentage distance from 52-week Low. |
| 24 | **`DAY_NAME`** | `Monday` to `Friday` | Name of the day of the week. |
| 25 | **`MONTH`** | `1` to `12` | Calendar month number. |
| 26 | **`QUARTER`** | `1` to `4` | Calendar quarter number. |
| 27 | **`WEEK`** | `1` to `53` | ISO calendar week number. |
| 28 | **`RSI_14`** | 14-period RSI | Relative Strength Index (0–100). |
| 29 | **`VWAP`** | `(HIGH + LOW + CLOSE) / 3` | Daily VWAP approximation. |
| 30 | **`EMA_20`** | 20-day EMA | 20-period Exponential Moving Average. |
| 31 | **`EMA_50`** | 50-day EMA | 50-period Exponential Moving Average. |
| 32 | **`EMA_100`** | 100-day EMA | 100-period Exponential Moving Average. |
| 33 | **`EMA_200`** | 200-day EMA | 200-period Exponential Moving Average. |
| 34 | **`EMA_400`** | 400-day EMA | 400-period Exponential Moving Average. |
| 35 | **`EMA_500`** | 500-day EMA | 500-period Exponential Moving Average. |
| 36 | **`MACD`** | `EMA(12) - EMA(26)` | MACD line. |
| 37 | **`MACD_SIGNAL`** | `EMA(MACD, 9)` | MACD signal line. |
| 38 | **`MACD_HIST`** | `MACD - MACD_SIGNAL` | MACD histogram. |
| 39 | **`MACD_CROSS`** | `'BULLISH'` / `'BEARISH'` / `'NO SIGNAL'` | MACD crossover signal. |
| 40 | **`MACD_TREND`** | `'POSITIVE MOMENTUM'` / `'NEGATIVE MOMENTUM'` | MACD histogram state. |
