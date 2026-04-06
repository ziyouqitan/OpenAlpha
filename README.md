# 🚀 OpenAlpha
> An Open-Source Alpha Mining Factory for the Chinese A-Share Market.一个开源的A股市场量化因子挖掘框架，持续更新中
> wechat:ziyouqitan，加我进量化交流群

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Market](https://img.shields.io/badge/Market-A--Share-red.svg)](#)
[![Execution](https://img.shields.io/badge/Execution-VWAP-orange.svg)](#)

## 📖 Strategy Overview
* **Universe:** China A-Shares CSI_500_INDEX.
* **Execution:** All Alphas are **delay 1** (T+1 execution) using **VWAP**.

Place the data folder in the root directory.
https://drive.google.com/drive/folders/1RRAKH0Pospp7o-RBLrXqWVYUav9F03-J?usp=drive_link




---

## 📊 Alpha Gallery

### Alpha 5000001
`ts_mean(vwap - close, 5)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/3bed5b43-76bb-4f57-b134-2e0ab534a155" width="900">
</p>

---

### Alpha 5000003
`cs_rank(cs_rank(open) - cs_rank(ts_delay(close, 1)))`

<p align="center">
  <img src="https://github.com/user-attachments/assets/0bc7e8a4-e665-4c26-985f-3a9d73a97685" width="900">
</p>

---

### Alpha 5000004
`ts_correlation(ts_ret(low, 1), ret1, 3)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/c64ed177-7dab-4ad2-ae7e-dcde0e30bfbf" width="900">
</p>

---

### Alpha 5000005
`ts_ols(open / ts_delay(close, 1), ts_delay(volume, 1), 10)[2]`

<p align="center">
  <img src="https://github.com/user-attachments/assets/425bc58f-f3d8-43eb-8c4a-acfdd376235c" width="900">
</p>

---

### Alpha 5000006
`-ts_ols(close, ret1, 10)[2]`

<p align="center">
  <img src="https://github.com/user-attachments/assets/3b0e7262-8d9e-465f-a579-6970f2f2d3c7" width="900">
</p>

---

### Alpha 5000009
`-ts_correlation(close, close / vwap - 1, 20)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/4f2a22d7-d939-4556-b078-bd2f5016ee43" width="900">
</p>

---

### Alpha 5000010
`ts_correlation(cs_rank(ts_delay(volume, 1)), cs_rank(ret1), 5)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/317de94c-849a-4d6b-9046-3cee9b273913" width="900">
</p>

---

### Alpha 5000011
`-close * volume * ts_zscore(ret1, 2)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/cde81214-6b4b-40b3-afa9-13c1257fcc82" width="900">
</p>

---

### Alpha 5000012
`ts_correlation(ret1, csi_500_ret1, 20)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/b97ad89d-a6c0-4c47-9d64-b13e1872b545" width="900">
</p>

---

### Alpha 5000013
`ts_ols(ret1, ts_delay(csi_500_ret1, 1), 5)[0]`

<p align="center">
  <img src="https://github.com/user-attachments/assets/4e3d8326-256d-4d2c-9ee5-f9cd56f9e1d9" width="900">
</p>

---

### Alpha 5000014
`ts_ols(ret1, ts_delay(ret1, 1), 20)[0]`

<p align="center">
  <img src="https://github.com/user-attachments/assets/db612e95-99ad-46bb-b322-99d3ab585071" width="900">
</p>

---

### Alpha 5000019
`cs_indneut(high - close, cs_group_quantile(at_mask(close, ts_fill(csi_500_weight) > 0), 10))`

<p align="center">
  <img src="https://github.com/user-attachments/assets/beb2c00b-f02f-4f6d-9619-3bccc645b840" width="900">
</p>

---

### Alpha 5000020
`ts_mean(at_mask(vwap - close, cs_rank(at_mask(volume, ts_fill(csi_500_weight) > 0)) > 0.5), 2)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/6a98788f-e3cc-4a5a-8236-eddbcb5e1f4e" width="900">
</p>

---

### Alpha 5000024
`ts_std(low/ts_delay(close,1)-1,100)-ts_std(high/ts_delay(close,1)-1,100)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/76d1489f-1170-4ef6-8fa2-a9b08e6a6fc3" width="900">
</p>

---

### Alpha 5000025
`cs_indneut(ts_mean(open-close,2),cs_group_quantile(at_mask(ts_std(close,2),ts_fill(csi_500_weight)>0),50))`

<p align="center">
  <img src="https://github.com/user-attachments/assets/039e2d88-fb8b-4378-80f7-8d38b743fe5f" width="900">
</p>

---

### Alpha 5000026
`ts_ols(csi_500_ret1,ret1,5)[0]`

<p align="center">
  <img src="https://github.com/user-attachments/assets/812f7b0a-4354-4dfc-a989-2e37d1dc5649" width="900">
</p>

---

### Alpha 5000029
`-ts_ols(ret1-csi_500_ret1,ret1,5)[0]`

<p align="center">
  <img src="https://github.com/user-attachments/assets/fcec5533-cf6d-4f2e-a23b-5641b89becd1" width="900">
</p>

---

### Alpha 5000030
`-ts_ols(ts_rank(close,10),ts_rank(np.abs(ret1),10),10)[0]`

<p align="center">
  <img src="https://github.com/user-attachments/assets/ef3076f2-781b-47b0-ba76-1f9446104ab5" width="900">
</p>

---

### Alpha 5000031
`-ts_ols(ts_rank(close,3),ts_rank(vwap,3),3)[2]`

<p align="center">
  <img src="https://github.com/user-attachments/assets/942105fc-7bdd-42bd-8154-6f572b83e0d0" width="900">
</p>

---

### Alpha 5000032
`-ts_regression(ts_rank(close,10),ts_rank(ret1,10),10,5)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/1b03e373-2a8b-4639-87fa-466984f09809" width="900">
</p>

---

### Alpha 5000033
`-ts_regression(csi_500_open/ts_delay(csi_500_close,1),close/ts_delay(close,1),10,4)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/4159f0dc-5ac8-4480-a269-5ab658c38299" width="900">
</p>

---

### Alpha 5000034
`ts_ols(ts_skewness(ret1,5),ret1,5)[0]`

<p align="center">
  <img src="https://github.com/user-attachments/assets/e6c0b3ba-1909-4009-bc37-a0a5ca56f121" width="900">
</p>

---

### Alpha 5000035
`-ts_regression(ts_skewness(ret1,3),ret1,7,9)`

<p align="center">
  <img src="https://github.com/user-attachments/assets/b6d09937-bf76-4904-b2ca-49f09a3f422e" width="900">
</p>

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
© 2026 OpenAlpha Team. 



