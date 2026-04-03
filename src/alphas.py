import warnings

# 忽略所有警告
warnings.filterwarnings("ignore")

import pickle
from tqdm import tqdm
import importlib
import simres.expr
importlib.reload(simres.expr)
from simres.expr import *

enddate='20251231'
with open ('ruiqiwang_csi_500.txt','r') as f:
    alpha_list=f.read().split('\n')


executor = AlphaExecutor(data_dir=f'../data/{enddate}')
executor.load_all_data()

for i in tqdm(range(len(alpha_list))):
    expr=alpha_list[i]
    alpha = executor.evaluate(f'at_nan2zero(cs_booksize(cs_rank(at_mask({expr},ts_fill(csi_500_weight)>0))-0.5))')
    pd.DataFrame(alpha,index=executor.context['stock_list'],columns=executor.context['datestr']).to_parquet(f"../alphas/{enddate}/matrix/"+str(5000001+i))
    btresult=executor.backtest(alpha)
    btresult['alpha_id']=str(5000001+i)
    with open(f"../alphas/{enddate}/simres/"+str(5000001+i)+".pkl", "wb") as f:
        pickle.dump(btresult, f)
    