# OpenAlpha
An Open-Source Alpha Mining Factory for the Chinese A-Share Market.
All Alphas are delay 1 and executed via VWAP.

ts_mean(vwap-close,5)
<img width="800" height="800" alt="5000001" src="https://github.com/user-attachments/assets/3bed5b43-76bb-4f57-b134-2e0ab534a155" />

cs_rank(cs_rank(open)-cs_rank(ts_delay(close,1)))
<img width="800" height="800" alt="5000003" src="https://github.com/user-attachments/assets/0bc7e8a4-e665-4c26-985f-3a9d73a97685" />

ts_correlation(ts_ret(low,1),ret1,3)
<img width="800" height="800" alt="5000004" src="https://github.com/user-attachments/assets/c64ed177-7dab-4ad2-ae7e-dcde0e30bfbf" />

ts_ols(open/ts_delay(close,1),ts_delay(volume,1),10)[2]
<img width="800" height="800" alt="5000005" src="https://github.com/user-attachments/assets/425bc58f-f3d8-43eb-8c4a-acfdd376235c" />

-ts_ols(close,ret1,10)[2]
<img width="800" height="800" alt="5000006" src="https://github.com/user-attachments/assets/3b0e7262-8d9e-465f-a579-6970f2f2d3c7" />

-ts_correlation(close,close/vwap-1,20)
<img width="800" height="800" alt="5000009" src="https://github.com/user-attachments/assets/4f2a22d7-d939-4556-b078-bd2f5016ee43" />

ts_correlation(cs_rank(ts_delay(volume,1)),cs_rank(ret1),5)
<img width="800" height="800" alt="5000010" src="https://github.com/user-attachments/assets/317de94c-849a-4d6b-9046-3cee9b273913" />

-close*volume*ts_zscore(ret1,2)
<img width="800" height="800" alt="5000011" src="https://github.com/user-attachments/assets/cde81214-6b4b-40b3-afa9-13c1257fcc82" />

ts_correlation(ret1,csi_500_ret1,20)
<img width="800" height="800" alt="5000012" src="https://github.com/user-attachments/assets/b97ad89d-a6c0-4c47-9d64-b13e1872b545" />

ts_ols(ret1,ts_delay(csi_500_ret1,1),5)[0]
<img width="800" height="800" alt="5000013" src="https://github.com/user-attachments/assets/4e3d8326-256d-4d2c-9ee5-f9cd56f9e1d9" />

ts_ols(ret1,ts_delay(ret1,1),20)[0]
<img width="800" height="800" alt="5000014" src="https://github.com/user-attachments/assets/db612e95-99ad-46bb-b322-99d3ab585071" />

cs_indneut(high-close,cs_group_quantile(at_mask(close,ts_fill(csi_500_weight)>0),10))
<img width="800" height="800" alt="5000019" src="https://github.com/user-attachments/assets/beb2c00b-f02f-4f6d-9619-3bccc645b840" />

ts_mean(at_mask(vwap-close,cs_rank(at_mask(volume,ts_fill(csi_500_weight)>0))>0.5),2)
<img width="800" height="800" alt="5000020" src="https://github.com/user-attachments/assets/6a98788f-e3cc-4a5a-8236-eddbcb5e1f4e" />

ts_std(low/ts_delay(close,1)-1,100)-ts_std(high/ts_delay(close,1)-1,100)
<img width="800" height="800" alt="5000024" src="https://github.com/user-attachments/assets/76d1489f-1170-4ef6-8fa2-a9b08e6a6fc3" />

cs_indneut(ts_mean(open-close,2),cs_group_quantile(at_mask(ts_std(close,2),ts_fill(csi_500_weight)>0),50))
<img width="800" height="800" alt="5000025" src="https://github.com/user-attachments/assets/039e2d88-fb8b-4378-80f7-8d38b743fe5f" />

ts_ols(csi_500_ret1,ret1,5)[0]
<img width="800" height="800" alt="5000026" src="https://github.com/user-attachments/assets/4c847764-ab06-41ab-a174-8f567fa99a7e" />

-ts_ols(ret1-csi_500_ret1,ret1,5)[0]
<img width="800" height="800" alt="5000029" src="https://github.com/user-attachments/assets/975d6906-3a60-4654-99c5-4c6ce325d15d" />

-ts_ols(ts_rank(close,10),ts_rank(np.abs(ret1),10),10)[0]
<img width="800" height="800" alt="5000030" src="https://github.com/user-attachments/assets/327019a9-1ad3-42b2-b0f6-9efdb9266609" />

-ts_ols(ts_rank(close,3),ts_rank(vwap,3),3)[2]
<img width="800" height="800" alt="5000031" src="https://github.com/user-attachments/assets/c9049206-3d00-4d16-bc51-2090346036b6" />

-ts_regression(ts_rank(close,10),ts_rank(ret1,10),10,5)
<img width="800" height="800" alt="5000032" src="https://github.com/user-attachments/assets/723d20de-f480-4fa1-a690-cc7fb4619eab" />

-ts_regression(csi_500_open/ts_delay(csi_500_close,1),close/ts_delay(close,1),10,4)
<img width="800" height="800" alt="5000033" src="https://github.com/user-attachments/assets/5f28df90-f385-4e0a-a26b-ce3dda0ee202" />

ts_ols(ts_skewness(ret1,5),ret1,5)[0]
<img width="800" height="800" alt="5000034" src="https://github.com/user-attachments/assets/12e3a660-ea53-4de5-9bcc-2a02044b16e9" />

-ts_regression(ts_skewness(ret1,3),ret1,7,9)
<img width="800" height="800" alt="5000035" src="https://github.com/user-attachments/assets/ae140e11-8d64-433d-93ef-567732510f6c" />



