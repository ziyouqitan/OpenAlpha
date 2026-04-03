# 🚀 OpenAlpha
> An Open-Source Alpha Mining Factory for the Chinese A-Share Market.

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Market](https://img.shields.io/badge/Market-A--Share-red.svg)](#)
[![Execution](https://img.shields.io/badge/Execution-VWAP-orange.svg)](#)

## 📖 Strategy Overview
* **Universe:** China A-Shares CSI_500_INDEX.
* **Execution:** All Alphas are **delay 1** (T+1 execution) using **VWAP**.
* **Goal:** High-frequency/Middle-frequency alpha generation based on price-volume data.

---

## 📊 Alpha Gallery

| ID | Formula (Alpha Expression) | Performance Backtest |
| :-- | :--- | :--- |
| **5000001** | `ts_mean(vwap - close, 5)` | <img src="https://github.com/user-attachments/assets/3bed5b43-76bb-4f57-b134-2e0ab534a155" width="400"> |
| **5000003** | `cs_rank(cs_rank(open) - cs_rank(ts_delay(close, 1)))` | <img src="https://github.com/user-attachments/assets/0bc7e8a4-e665-4c26-985f-3a9d73a97685" width="400"> |
| **5000004** | `ts_correlation(ts_ret(low, 1), ret1, 3)` | <img src="https://github.com/user-attachments/assets/c64ed177-7dab-4ad2-ae7e-dcde0e30bfbf" width="400"> |
| **5000005** | `ts_ols(open / ts_delay(close, 1), ts_delay(volume, 1), 10)[2]` | <img src="https://github.com/user-attachments/assets/425bc58f-f3d8-43eb-8c4a-acfdd376235c" width="400"> |
| **5000006** | `-ts_ols(close, ret1, 10)[2]` | <img src="https://github.com/user-attachments/assets/3b0e7262-8d9e-465f-a579-6970f2f2d3c7" width="400"> |
| **5000009** | `-ts_correlation(close, close / vwap - 1, 20)` | <img src="https://github.com/user-attachments/assets/4f2a22d7-d939-4556-b078-bd2f5016ee43" width="400"> |
| **5000010** | `ts_correlation(cs_rank(ts_delay(volume, 1)), cs_rank(ret1), 5)` | <img src="https://github.com/user-attachments/assets/317de94c-849a-4d6b-9046-3cee9b273913" width="400"> |
| **5000011** | `-close * volume * ts_zscore(ret1, 2)` | <img src="https://github.com/user-attachments/assets/cde81214-6b4b-40b3-afa9-13c1257fcc82" width="400"> |
| **5000012** | `ts_correlation(ret1, csi_500_ret1, 20)` | <img src="https://github.com/user-attachments/assets/b97ad89d-a6c0-4c47-9d64-b13e1872b545" width="400"> |
| **5000013** | `ts_ols(ret1, ts_delay(csi_500_ret1, 1), 5)[0]` | <img src="https://github.com/user-attachments/assets/4e3d8326-256d-4d2c-9ee5-f9cd56f9e1d9" width="400"> |
| **5000014** | `ts_ols(ret1, ts_delay(ret1, 1), 20)[0]` | <img src="https://github.com/user-attachments/assets/db612e95-99ad-46bb-b322-99d3ab585071" width="400"> |
| **5000019** | `cs_indneut(high - close, cs_group_quantile(at_mask(close, ts_fill(csi_500_weight) > 0), 10))` | <img src="https://github.com/user-attachments/assets/beb2c00b-f02f-4f6d-9619-3bccc645b840" width="400"> |
| **5000020** | `ts_mean(at_mask(vwap - close, cs_rank(at_mask(volume, ts_fill(csi_500_weight) > 0)) > 0.5), 2)` | <img src="https://github.com/user-attachments/assets/6a98788f-e3cc-4a5a-8236-eddbcb5e1f4e" width="400"> |
| **5000024** | `ts_std(low/ts_delay(close,1)-1,100)-ts_std(high/ts_delay(close,1)-1,100)` | <img src="https://github.com/user-attachments/assets/76d1489f-1170-4ef6-8fa2-a9b08e6a6fc3" width="400"> |
| **5000025** | `cs_indneut(ts_mean(open-close,2), cs_group_quantile(...))` | <img src="https://github.com/user-attachments/assets/039e2d88-fb8b-4378-80f7-8d38b743fe5f" width="400"> |

---

## 🛠 Operators Manual
To replicate these Alphas, ensure you have the following basic operators:
- `ts_mean(x, d)`: Time-series mean over `d` days.
- `cs_rank(x)`: Cross-sectional rank.
- `ts_ols(y, x, d)`: Rolling OLS regression return `[0]alpha, [1]beta, [2]residual`.
- `cs_indneut(x, g)`: Industry/Group neutralization.

## 🤝 Contribution
Welcome to submit your Alphas via Pull Requests! 

---
© 2026 OpenAlpha Team. Managed by Gemini Factory.



