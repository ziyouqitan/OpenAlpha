import os
import sys
import inspect
import pickle
import traceback
import numpy as np
import pandas as pd
import bottleneck as bn
import matplotlib.pyplot as plt
import matplotlib.dates as mdates




# --- 自动路径挂载 ---
try:
    curr_path = os.path.dirname(os.path.abspath(__file__))
except NameError:
    curr_path = os.getcwd()

if curr_path not in sys.path:
    sys.path.insert(0, curr_path)

# 尝试导入你的算子库
try:
    import operators as op
except ImportError:
    print("警告: 未找到 op 模块，请确保目录结构正确。")
    op = None

class AlphaExecutor:
    def __init__(self, data_dir,alpha_dir=None):
        self.data_dir = data_dir
        self.alpha_dir = alpha_dir
        self.context = {}
        self.alpha_pool=[]
        self.alpha_matrix=[]
        self.data_loaded = False
    def load_all_simres(self):
        if not os.path.exists(self.alpha_dir):
            raise FileNotFoundError(f"Alpha目录 {self.alpha_dir} 不存在")

        print(f"--- 正在初始化数据引擎 ---")
        for file in os.listdir(os.path.join(self.alpha_dir,'simres')):
            file_path = os.path.join(self.alpha_dir,'simres', file)
            # 过滤掉小于 1KB 的无用文件
            if os.path.getsize(file_path) < 1024:
                continue
            name = os.path.splitext(file)[0]
            try:
                with open(file_path, "rb") as f:
                    simres_result = pickle.load(f)
                if 'alpha_id' not in simres_result:
                    simres_result['alpha_id']=name
                self.alpha_pool.append(simres_result)
                print('success load alpha simres'+name)
            except:
                print('fail to load alpha simres'+name)
    def load_all_alphas(self):
        if not os.path.exists(self.alpha_dir):
            raise FileNotFoundError(f"Alpha目录 {self.alpha_dir} 不存在")

        print(f"--- 正在初始化数据引擎 ---")
        for file in os.listdir(os.path.join(self.alpha_dir,'matrix')):
            file_path = os.path.join(self.alpha_dir,'matrix', file)
            # 过滤掉小于 1KB 的无用文件
            if os.path.getsize(file_path) < 1024:
                continue
            name = os.path.splitext(file)[0]
            try:
                matrix=pd.read_parquet(file_path).values.astype(np.float32)
                self.alpha_matrix.append(matrix)
                print('success load alpha matrix'+name)
            except:
                print('fail to load alpha matrix'+name)
    def corr(self,simres):
        alpha_pool=self.alpha_pool.copy()
        alpha_pool.append(simres)
        corr_matrix=np.corrcoef([item['net_ret'] for item in alpha_pool])[-1]
        result_pool=[]
        for i in range(len(alpha_pool)-1):
            start_date=alpha_pool[i]['datestr'][0]
            end_date=alpha_pool[i]['datestr'][-1]
            simres_result=self.simres_cut(alpha_pool[i], start_date, end_date,if_plot=False)
            simres_result['corr']=corr_matrix[i]
            simres_result['alpha_id']=alpha_pool[i]['alpha_id']
            result_pool.append(simres_result)
        print(pd.DataFrame(result_pool).sort_values('corr',ascending=False).iloc[:5])
        return result_pool


        
    def load_all_data(self):
        """
        一键载入 data 文件夹下的所有文件 (csv/parquet)
        自动将 DataFrame 转为 (Stock, Date) 的 float32 矩阵
        """
        if not os.path.exists(self.data_dir):
            raise FileNotFoundError(f"数据目录 {self.data_dir} 不存在")

        print(f"--- 正在初始化数据引擎 ---")
        for file in os.listdir(self.data_dir):
            file_path = os.path.join(self.data_dir, file)
            # 过滤掉小于 1KB 的无用文件
            if os.path.getsize(file_path) < 1024:
                continue

            name = os.path.splitext(file)[0]
            if name=='pv':
                continue
            try:
                
                df = pd.read_parquet(file_path)
                
                # 统一转为 float32 以节省内存，形状保持 (Stock, Date)
                if name in {'datestr','stock_list'}:
                    self.context[name] = df.values.reshape(-1)
                else:
                    self.context[name] = df.values.astype(np.float32)
                print(f"已加载字段: [{name}] | 形状: {self.context[name].shape}")
            except Exception:
                print(f"载入 {file} 失败")
                traceback.print_exc()
        
        self.context['csi_500_vwap']=self.context['csi_500_amount']/self.context['csi_500_volume']*10
        self.context['vwap']=self.context['amount']/self.context['volume']*10
        self.context['ret1']=op.ts_ret(self.context['close'],1)
        self.context['csi_500_ret1']=op.ts_ret(self.context['csi_500_close'],1)
        self.context['csi_500_vwap_ret1']=op.ts_ret(self.context['csi_500_vwap'],1)

        
        # 注入 NumPy 命名空间
        self.context['np'] = np
        self.context['bn'] = bn
        self.context.update({n: getattr(np, n) for n in dir(np) if not n.startswith('_')})
        
        # 语义化轴定义
        self.context['CS'] = 0 # 截面轴
        self.context['TS'] = 1 # 时序轴

        # 一键注入自定义算子
        if op:
            custom_ops = {k: v for k, v in inspect.getmembers(op, inspect.isfunction) 
                         if not k.startswith('_')}
            self.context.update(custom_ops)
            print(f"已注入自定义算子: {list(custom_ops.keys())}")

        self.data_loaded = True
        print(f"--- 引擎就绪 ---\n")

    def evaluate(self, expression):
        """
        执行表达式计算
        """
        if not self.data_loaded:
            self.load_all_data()

        try:
            # 限制执行环境，防止恶意调用
            result = eval(expression, {"__builtins__": None}, self.context)
            return result
        except Exception:
            print(f"表达式执行错误: {expression}")
            traceback.print_exc()
            return None

    def backtest(self,alpha,price='vwap'):
        """
        基于 VWAP-to-VWAP 的回测与可视化
        :param alpha: np.ndarray (Stock, Date), 因子原始值
        :param vwap: np.ndarray (Stock, Date), VWAP价格
        :param dates: pd.DatetimeIndex, 对应 Date 维度
        """
        try:
            # 1. 计算收益率矩阵 (t+1 VWAP / t VWAP - 1)
            # 结果形状 (Stock, Date-1)
            vwap=self.context[price]
            dates = pd.to_datetime(self.context['datestr'])
            asset_ret = op.ts_ret(vwap,1)
            
            # 2. 因子处理：截面归一化 (Booksize 逻辑)
            # 假设原始因子越大越看多
            weights = op.ts_delay(alpha,2) # t日权重对应 t->t+1 的收益

            pos_mask = np.where(weights > 0, weights, 0)
            neg_mask = np.where(weights < 0, weights, 0)
            
            # 归一化：多头和空头各自权重和为 1
            long_w = pos_mask / np.nansum(pos_mask, axis=0)
            short_w = neg_mask / np.abs(np.nansum(neg_mask, axis=0))

            daily_tvr=np.nansum(np.abs(op.ts_delta(long_w+short_w,1)),axis=0)/2
            long_num=np.nansum(np.where(long_w>0,1,0),axis=0)
            short_num=np.nansum(np.where(short_w<0,1,0),axis=0)
            # 3. 计算三条曲线的每日收益
            long_daily = np.nansum(long_w * asset_ret, axis=0)
            short_daily = np.nansum(short_w * asset_ret, axis=0)
            net_daily = long_daily + short_daily # 对冲收益
            
            # # 4. 计算累计收益 (假设初始资金 10000)
            # scale = 10000
            # long_pnl = np.nancumsum(long_daily) * scale
            # short_pnl = np.nancumsum(short_daily) * scale
            # net_strategy = np.nancumsum(net_daily) * scale
            

            
            # # 对齐日期 (因为收益率少了一天)
            # plot_dates = dates
            
            # # 5. 计算量化指标 (用于 Title)
            # ann_ret = np.nanmean(net_daily) * 252
            # ann_vol = np.nanstd(net_daily) * np.sqrt(252)
            # sr = ann_ret / ann_vol if ann_vol != 0 else 0
            # dd = (np.maximum.accumulate(net_strategy) - net_strategy).max() / scale * 100 # 简单回撤%
            # tvr=np.nanmean(daily_tvr)

            
            # # 6. 绘图逻辑 (按你提供的样式)
            # fig, ax = plt.subplots(figsize=(8, 8))
            # fig.patch.set_linewidth(2)
            # fig.patch.set_edgecolor('black') 
            # ax.set_facecolor('white')
            # ax.grid(True, which='both', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.5)
    
            # # 绘图
            # ax.plot(plot_dates, long_pnl, color='black', label='Long', linewidth=0.8, alpha=0.8)
            # ax.plot(plot_dates, short_pnl, color='green', label='Short', linewidth=0.8, alpha=0.8)
            # ax.plot(plot_dates, net_strategy, color='red', label='ls', linewidth=1.5, zorder=5)
    
            # # 格式化
            # ax.xaxis.set_major_locator(mdates.YearLocator())
            # ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
            # plt.xticks(rotation=30, ha='right', fontsize=8)
            
            # # 动态生成 Header
            # header = (f"sr:{sr:.3f} ret:{ann_ret:.3f} tvr:{tvr:.3f} num:{int(np.nanmean(op.at_zero2nan(long_num)))}|{int(np.nanmean(op.at_zero2nan(short_num)))} dd:{dd:.1f}" f"({plot_dates[0].strftime('%Y%m%d')}-{plot_dates[-1].strftime('%Y%m%d')})")
            # plt.title(header, loc='left', fontsize=10, family='monospace', pad=15)
            
            # ax.set_ylabel('Thousand Currencies', fontsize=8)
            # ax.legend(loc='upper left', fontsize=7, frameon=True, edgecolor='lightgray')
            # ax.set_xlim(plot_dates[0], plot_dates[-1])
            
            # plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
            # plt.show()
            
            return {
                    'datestr':self.context['datestr'],
                    'net_ret':net_daily,
                    'long_ret':long_daily,
                    'short_ret':short_daily,
                    'tvr':daily_tvr,
                    'long_num':long_num,
                    'short_num':short_num,
                   } 
    
        except Exception:
            traceback.print_exc()
    def simres_cut(self,res, start_date, end_date,if_plot=True,index=None,alpha_id=None,save_path=None):
        """
        对回测结果进行区间切片并重新绘图
        :param res: backtest 函数返回的 dict
        :param start_date: 起始日期 字符串 e.g. '20180101'
        :param end_date: 结束日期 字符串 e.g. '20191231'
        """
        try:
            if 'alpha_id' in res:
                alpha_id=res['alpha_id']
            # 1. 提取原始数据
            dates = pd.to_datetime(res['datestr'])
            net_daily = res['net_ret']
            long_daily = res['long_ret']
            short_daily = res['short_ret']
            daily_tvr = res['tvr']
            long_num = res['long_num']
            short_num = res['short_num']
            if index!=None:
                short_daily = self.context[index][0]
                net_daily = long_daily-short_daily


            
            # 2. 构造切片掩码
            mask = (dates >= pd.to_datetime(start_date)) & (dates <= pd.to_datetime(end_date))
            
            if not np.any(mask):
                print(f"Error: No data found between {start_date} and {end_date}")
                return
    
            # 3. 切片数据
            cut_dates = dates[mask]
            cut_net = net_daily[mask]
            cut_long = long_daily[mask]
            cut_short = short_daily[mask]
            cut_tvr = daily_tvr[mask]
            cut_long_num = long_num[mask]
            cut_short_num = short_num[mask]
    
            # 4. 重新计算区间累计收益与指标
            scale = 10000
            # 重新从 0 开始计算累计值
            long_pnl = np.nancumsum(cut_long) * scale
            short_pnl = np.nancumsum(cut_short) * scale
            net_strategy = np.nancumsum(cut_net) * scale
    
            ann_ret = np.nanmean(cut_net) * 252
            ann_vol = np.nanstd(cut_net) * np.sqrt(252)
            sr = ann_ret / ann_vol if ann_vol != 0 else 0
            dd = (np.maximum.accumulate(net_strategy) - net_strategy).max() / scale * 100
            tvr_avg = np.nanmean(cut_tvr)
            
            # 处理平均票数 (复用你 at_zero2nan 的逻辑)
            def at_zero2nan(x): return np.where(x == 0, np.nan, x)
            avg_l_num = int(np.nanmean(at_zero2nan(cut_long_num))) if np.any(cut_long_num) else 0
            avg_s_num = int(np.nanmean(at_zero2nan(cut_short_num))) if np.any(cut_short_num) else 0
            if if_plot:
                # 5. 绘图 (复用 backtest 样式)
                fig, ax = plt.subplots(figsize=(8, 8))
                fig.patch.set_linewidth(2)
                fig.patch.set_edgecolor('black')
                ax.set_facecolor('white')
                ax.grid(True, which='both', color='lightgray', linestyle='--', linewidth=0.5, alpha=0.5)
        
                ax.plot(cut_dates, long_pnl, color='black', label='Long', linewidth=0.8, alpha=0.8)
                ax.plot(cut_dates, short_pnl, color='green', label='Short', linewidth=0.8, alpha=0.8)
                ax.plot(cut_dates, net_strategy, color='red', label=('' if alpha_id==None else alpha_id), linewidth=1.5, zorder=5)
        
                # 格式化
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y%m%d'))
                plt.xticks(rotation=30, ha='right', fontsize=8)
        
                header = (f"sr:{sr:.3f} ret:{ann_ret:.3f} tvr:{tvr_avg:.3f} "
                          f"num:{avg_l_num}|{avg_s_num} dd:{dd:.1f} "
                          f"({cut_dates[0].strftime('%Y%m%d')}-{cut_dates[-1].strftime('%Y%m%d')})")
                plt.title(header, loc='left', fontsize=10, family='monospace', pad=15)
        
                ax.set_ylabel('Thousand Currencies', fontsize=8)
                ax.legend(loc='upper left', fontsize=7, frameon=True, edgecolor='lightgray')

                # --- 强制设置起始和结束日期刻度 ---
                # 选取 5-6 个均匀分布的中间点 + 明确的起点和终点
                num_ticks = 7
                if len(cut_dates) > num_ticks:
                    # 选取均匀分布的索引
                    idx = np.linspace(0, len(cut_dates) - 1, num_ticks).astype(int)
                    display_dates = cut_dates[idx]
                else:
                    display_dates = cut_dates
                
                # 设置刻度位置和标签
                ax.set_xticks(display_dates)
                ax.set_xticklabels([d.strftime('%Y%m%d') for d in display_dates], 
                                   rotation=30, ha='right', fontsize=8)
                
                # 确保 X 轴范围严格对齐
                ax.set_xlim(cut_dates[0], cut_dates[-1])

                

        
                plt.tight_layout(rect=[0.02, 0.02, 0.98, 0.98])
                if save_path!=None:
                    plt.savefig(save_path)
                plt.show()

            return {
                'ann_ret':ann_ret,
                'ann_vol':ann_vol,
                'sr':sr,
                'dd':dd,
                'tvr_avg':tvr_avg,
            }
    
        except Exception:
            traceback.print_exc()
            
    
# --- 快速运行脚本 ---
if __name__ == "__main__":
    # 1. 初始化执行器
    executor = AlphaExecutor(data_dir='./data')
    
    # 2. 定义测试表达式
    # 假设 data 下有 close.csv 和 volume.csv
    test_formulas = [
        "cs_zscore(ts_mean(close, 20) / ts_delay(close, 1) - 1)",
        "ts_correlation(close, volume, 10)",
        "np.where(close > ts_delay(close, 1), 1, -1)"
    ]
    
    # 3. 循环计算并保存结果
    for i, formula in enumerate(test_formulas):
        alpha_res = executor.evaluate(formula)
        if alpha_res is not None:
            print(f"Alpha_{i} 计算完成，均值: {np.nanmean(alpha_res):.4f}")
            # 这里可以接你之前的 backtest 函数