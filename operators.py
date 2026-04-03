import numpy as np
import bottleneck as bn
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view

def at_zero2nan(arr):
    return np.where(arr==0,np.nan,arr)
def at_nan2zero(arr):
    return np.where(np.isnan(arr),0,arr)
def at_mask(alpha, mask):
    """
    基础掩码过滤 (Minimal Vectorized Mask)
    
    参数:
    ----------
    alpha : np.ndarray (Stock, Date) - 原始因子值
    mask : np.ndarray (Stock, Date) - 布尔矩阵 (True表示可交易/有效)
    
    返回:
    -------
    np.ndarray : 过滤后的因子矩阵
    """
    # 强制将所有 mask 为 False 的位置设为 NaN
    # 这样后续的 np.nansum, np.nanmean, cs_rank 都会自动跳过这些位置
    return np.where(mask, alpha, np.nan)

def ts_skewness(alpha, window):
    """
    时间序列滚动偏度 (Rolling Skewness)
    :param alpha: np.ndarray (Stock, Date)
    :param window: 窗口大小 (int)
    :return: 滚动偏度矩阵 (Stock, Date)
    """
    n_stocks, n_dates = alpha.shape
    res = np.full_like(alpha, np.nan)
    
    if window < 3: # 样本量太小无法计算偏度
        return res

    # 1. 创建滑动窗口视图 (Stock, Date-window+1, window)
    v = sliding_window_view(alpha, window, axis=1)
    
    # 2. 计算各阶中心矩 (利用 nanmean 处理缺失值)
    mu = np.nanmean(v, axis=-1, keepdims=True)
    diff = v - mu
    
    # 二阶矩 (方差的平均值)
    m2 = np.nanmean(diff**2, axis=-1)
    # 三阶矩
    m3 = np.nanmean(diff**3, axis=-1)
    
    # 3. 计算偏度: Skew = m3 / (m2^1.5)
    # 使用 np.errstate 避免除以 0 导致的警告
    with np.errstate(divide='ignore', invalid='ignore'):
        skew = m3 / (m2**1.5)
    
    # 4. 填充结果，对齐原始 Date 维度
    res[:, window-1:] = skew
    
    return res

def ts_kurtosis(alpha, window):
    """
    时间序列滚动峰度 (Excess Kurtosis)
    :param alpha: np.ndarray (Stock, Date)
    :param window: 窗口大小 (int)
    :return: 滚动超额峰度矩阵
    """
    n_stocks, n_dates = alpha.shape
    res = np.full_like(alpha, np.nan)
    
    if window < 4: # 样本量太小无法计算峰度
        return res

    # 1. 创建滑动窗口视图
    v = sliding_window_view(alpha, window, axis=1)
    
    # 2. 计算各阶中心矩
    mu = np.nanmean(v, axis=-1, keepdims=True)
    diff = v - mu
    
    # 二阶矩 (方差)
    m2 = np.nanmean(diff**2, axis=-1)
    # 四阶矩
    m4 = np.nanmean(diff**4, axis=-1)
    
    # 3. 计算超额峰度 (Fisher's definition)
    # 避免除以 0 (方差为 0 的情况)
    with np.errstate(divide='ignore', invalid='ignore'):
        kurt = m4 / (m2**2) - 3
    
    # 4. 填充结果
    res[:, window-1:] = kurt
    
    return res
def ts_fill(alpha, window=None):
    """
    基于 NumPy 的高性能时序填充算子 (AlphaFactory Core)
    适用于输入形状为 (Stock, Date) 的矩阵
    """
    # 1. 初始化
    out = np.array(alpha, copy=True)
    mask = ~np.isnan(out)
    
    # 构建列索引矩阵 (对应 Date 维度)
    # 形状为 (1, N_dates)，利用广播匹配所有股票
    cols = np.arange(out.shape[1])[None, :]
    
    # 2. 核心索引累积逻辑 (沿 axis=1，即向右传播时间)
    # idx 记录的是截止到当前列，左侧最近的一个非 NaN 值的列索引
    idx = np.where(mask, cols, 0)
    idx = np.maximum.accumulate(idx, axis=1)
    
    # 3. 执行初步填充 (利用高级索引)
    # 获取每一行对应的过去最近有效值
    # np.arange(out.shape[0])[:, None] 负责选中每一行(Stock)
    res = out[np.arange(out.shape[0])[:, None], idx]
    
    # 4. 边界与窗口约束处理
    # a) 处理左侧从未出现过有效值的区域
    first_valid_mask = np.maximum.accumulate(mask, axis=1)
    res[~first_valid_mask] = np.nan
    
    # b) 如果设置了 window，检查填充跨度
    if window is not None:
        # 计算当前列索引与引用值列索引的差值
        distance = cols - idx
        res[distance > window] = np.nan
        
    return res
def ts_rank(alpha, window):
    """
    时间序列滚动排名 (Rolling Rank)
    :param alpha: np.ndarray (Stock, Date)
    :param window: 窗口大小 (int)
    :return: 归一化到 [0, 1] 的排名矩阵
    """
    # bn.move_rank 直接在滑动窗口内计算排名
    # 返回值范围默认是 [-1, 1] 或 [1, window] 
    # 取决于具体版本，我们统一归一化处理
    
    # move_rank 会自动处理轴向，axis=1 代表在时间维度滚动
    ranks = bn.move_rank(alpha, window=window, axis=1)
    
    # 归一化到 [0, 1]
    # 公式: (rank_current - min_rank) / (max_rank - min_rank)
    # move_rank 默认返回的是 [-1, 1] 之间的值
    # 映射逻辑：(ranks + 1) / 2
    return (ranks + 1) / 2
def ts_min(alpha, window):
    return bn.move_min(alpha, window=window, axis=1)
def ts_max(alpha, window):
    return bn.move_max(alpha, window=window, axis=1)
def ts_mean(arr, window):
    """
    时间序列滚动平均 (Time-Series Mean)
    :param arr: np.ndarray, 形状为 (n_obs, n_assets)，纵轴为时间
    :param window: int, 滚动窗口大小
    :return: np.ndarray, 形状与输入一致
    """
    # axis=0 表示沿着时间轴滑动
    # min_count=window 表示窗口内必须满 window 个数才计算，否则填 NaN
    # 如果你想只要有数据就计算，可以将 min_count 设为 1
    return bn.move_mean(arr, window=window, min_count=window, axis=1)
def ts_sum(alpha, window):
    return bn.move_sum(alpha, window=window, axis=1)
def ts_std(arr, window):
    """
    时间序列滚动标准差
    :param arr: np.ndarray, 形状 (n_obs, n_assets)
    :param window: 滚动窗口大小
    :return: 滚动标准差矩阵，形状与输入一致
    """
    # axis=0 表示沿着时间轴（纵向）滑动
    # min_count=window 表示窗口内数据必须填满才计算，否则返回 NaN
    return bn.move_std(arr, window=window, min_count=window, axis=1)
def ts_zscore(arr,window):
    return ts_mean(arr,window)/ts_std(arr,window)
def ts_delay(arr, shift):
    result = np.roll(arr, shift,axis=1)
    if shift > 0:
        result[:,:shift] = np.nan
    elif shift < 0:
        result[:,shift:] = np.nan
    return result

def ts_delta(arr,shift):
    return arr-ts_delay(arr,shift)
def ts_ret(arr,shift):
    return ts_delta(arr,shift)/ts_delay(arr,shift)
def ts_correlation(x, y, window):
    """
    高性能 NumPy 版滚动相关性
    x, y: np.ndarray (Time x Assets)
    """
    # 均值
    mean_x = bn.move_mean(x, window=window, min_count=window, axis=1)
    mean_y = bn.move_mean(y, window=window, min_count=window, axis=1)
    
    # 协方差的分子部分 E[XY] - E[X]E[Y]
    cov_xy = bn.move_mean(x * y, window=window, min_count=window, axis=1) - mean_x * mean_y
    
    # 标准差 (std_x * std_y)
    std_x = bn.move_std(x, window=window, min_count=window, axis=1)
    std_y = bn.move_std(y, window=window, min_count=window, axis=1)
    
    # 相关系数
    return np.divide(cov_xy, std_x * std_y, out=np.full_like(x, np.nan), where=(std_x * std_y) != 0)



def ts_ols(y, x, window):
    """
    向量化滚动 OLS 回归 (y = beta * x + alpha + eps)
    :param y: np.ndarray (Stock, Date) - 因变量 (如未来收益)
    :param x: np.ndarray (Stock, Date) - 自变量 (如因子值或市场收益)
    :param window: 窗口大小 (int)
    :return: beta, alpha, residuals (形状均为 Stock, Date)
    """
    n_stocks, n_dates = y.shape
    beta = np.full_like(y, np.nan)
    alpha = np.full_like(y, np.nan)
    res = np.full_like(y, np.nan)
    
    if window > n_dates:
        return beta, alpha, res

    # 1. 创建滑动窗口视图 (Stock, Date-window+1, window)
    y_view = sliding_window_view(y, window, axis=1)
    x_view = sliding_window_view(x, window, axis=1)

    # 2. 计算均值 (用于中心化，简化计算)
    y_mean = np.mean(y_view, axis=-1)
    x_mean = np.mean(x_view, axis=-1)
    
    # 3. 计算离差平方和与协方差
    # Cov(x, y) = E[xy] - E[x]E[y]
    # Var(x) = E[x^2] - (E[x])^2
    sum_xy = np.sum(x_view * y_view, axis=-1)
    sum_xx = np.sum(x_view * x_view, axis=-1)
    
    # 根据最小二乘法公式: beta = (sum(xy) - n*mean_x*mean_y) / (sum(x^2) - n*mean_x^2)
    # 分母 (n * Var(x))
    denominator = sum_xx - window * (x_mean ** 2)
    
    # 避免除以 0
    valid_mask = np.abs(denominator) > 1e-12
    
    # 计算 Beta
    curr_beta = np.divide(sum_xy - window * x_mean * y_mean, 
                          denominator, 
                          out=np.zeros_like(sum_xy), 
                          where=valid_mask)
    
    # 计算 Alpha (截距): alpha = mean_y - beta * mean_x
    curr_alpha = y_mean - curr_beta * x_mean
    
    # 4. 填充结果 (对齐原始维度)
    beta[:, window-1:] = curr_beta
    alpha[:, window-1:] = curr_alpha
    
    # 5. 计算残差: res = y - (beta * x + alpha)
    # 注意这里计算的是全量残差，如果只需要窗口最后一天的残差可做切片
    res = y - (beta * x + alpha)

    return beta, alpha, res



def ts_regression(x, y, window, rettype=0):
    """
    x, y: np.ndarray, 形状为 (N, M)
    window: 滚动窗口大小
    rettype: 返回类型 0-9
    返回: np.ndarray, 形状与输入一致 (N, M)
    """
    x = np.asanyarray(x)
    y = np.asanyarray(y)
    n, m = x.shape
    
    # 初始化与输入同形状的空矩阵
    output = np.full((n, m), np.nan)
    
    if n < window:
        return output

    # 1. 构造滑动窗口视图
    # axis=0 表示只在时间轴上滑动
    # 结果形状: (n-window+1, m, window)
    x_wins = sliding_window_view(x, window, axis=0)
    y_wins = sliding_window_view(y, window, axis=0)
    
    # 2. 计算窗口统计量 (针对最后两个维度操作: m 是列, window 是时间窗口)
    # 计算均值时在 axis=2 (window轴) 上操作
    x_mean = np.mean(x_wins, axis=2, keepdims=True)
    y_mean = np.mean(y_wins, axis=2, keepdims=True)
    
    x_diff = x_wins - x_mean
    y_diff = y_wins - y_mean
    
    sum_x_diff_sq = np.sum(x_diff**2, axis=2)
    sum_xy_diff = np.sum(x_diff * y_diff, axis=2)
    
    # 3. 计算核心系数 Beta & Alpha
    with np.errstate(divide='ignore', invalid='ignore'):
        beta = sum_xy_diff / sum_x_diff_sq  # 形状 (n-window+1, m)
        alpha = y_mean.squeeze(axis=2) - beta * x_mean.squeeze(axis=2)
    
    # 4. 根据 rettype 计算结果
    res_data = None
    
    if rettype == 2: # Beta
        res_data = beta
    elif rettype == 1: # Alpha
        res_data = alpha
    elif rettype == 0: # Residuals (当前点)
        y_curr = y[window-1:]
        x_curr = x[window-1:]
        res_data = y_curr - (beta * x_curr + alpha)
    elif rettype == 3: # Predicted Y
        x_curr = x[window-1:]
        res_data = beta * x_curr + alpha
    else:
        # 涉及 SSE/SST 的复杂指标计算
        y_hat_wins = beta[..., np.newaxis] * x_wins + alpha[..., np.newaxis]
        sse = np.sum((y_wins - y_hat_wins)**2, axis=2)
        sst = np.sum((y_wins - y_mean)**2, axis=2)
        
        if rettype == 4: res_data = sse
        elif rettype == 5: res_data = sst
        elif rettype == 6: 
            with np.errstate(divide='ignore', invalid='ignore'):
                res_data = 1 - sse/sst
        elif rettype == 7: 
            res_data = sse / (window - 2)
        elif rettype == 8: # SE(Alpha)
            s2 = sse / (window - 2)
            res_data = np.sqrt(s2 * (1/window + np.squeeze(x_mean**2, axis=2) / sum_x_diff_sq))
        elif rettype == 9: # SE(Beta)
            s2 = sse / (window - 2)
            res_data = np.sqrt(s2 / sum_x_diff_sq)

    # 5. 将结果填回原始维度的矩阵中
    if res_data is not None:
        output[window-1:] = res_data
        
    return output


def cs_zscore(alpha):
    return (alpha-np.nanmean(alpha,axis=0))/np.nanstd(alpha,axis=0)
def cs_booksize(alpha):
    long=np.where(alpha>0,alpha,0)
    short=np.where(alpha<0,alpha,0)
    long=long/np.nansum(long,axis=0)
    short=short/np.nansum(short,axis=0)
    return at_nan2zero(long)-at_nan2zero(short)



def cs_indneut(alpha, ind_matrix):
    """
    完全向量化的行业中性化 (无 Python 层的 for 循环)
    输入 alpha, ind_matrix 均为 (Stock, Date)
    """
    n_stocks, n_dates = alpha.shape
    
    # 1. 处理 NaN：将所有 NaN 转换为 0 (或特定的 ID)，并记录掩码
    # 注意：ind_matrix 必须是整数类型
    mask = ~np.isnan(alpha) & ~np.isnan(ind_matrix)
    clean_alpha = np.where(mask, alpha, 0)
    clean_ind = np.where(mask, ind_matrix, 0).astype(int)
    
    # 2. 构造二维偏移量，将 (Stock, Date) 展平为一维索引
    # 这样我们可以一次性对所有时间点进行分组求和
    # 偏移量计算：industry_id + date_index * max_industry_id
    max_ind = int(np.nanmax(ind_matrix)) + 1
    offset = np.arange(n_dates) * max_ind
    flat_ind = (clean_ind + offset[None, :]).flatten()
    
    # 3. 使用 bincount 一次性计算所有“行业-日期”组合的和与计数
    # 结果是一个长度为 (n_dates * max_ind) 的一维数组
    flat_alpha = clean_alpha.flatten()
    comb_sums = np.bincount(flat_ind, weights=flat_alpha, minlength=n_dates * max_ind)
    comb_counts = np.bincount(flat_ind, minlength=n_dates * max_ind)
    
    # 4. 计算均值并映射回原始形状
    # 避免除以 0
    comb_means = np.divide(comb_sums, comb_counts, 
                           out=np.zeros_like(comb_sums), 
                           where=comb_counts != 0)
    
    # 5. 核心：通过 flat_ind 索引把均值“广播”回每个 Stock-Date 位置
    # 并从原始 alpha 中减去
    pixel_means = comb_means[flat_ind].reshape(n_stocks, n_dates)
    
    return np.where(mask, alpha - pixel_means, np.nan)


def cs_rank(alpha):
    """
    完全向量化的截面排序 (无 Python 循环)
    输入 alpha 形状为 (Stock, Date)
    """
    n_stocks, n_dates = alpha.shape
    
    # 1. 记录 NaN 掩码
    mask = ~np.isnan(alpha)
    
    # 2. 准备结果矩阵
    ranked = np.full_like(alpha, np.nan)
    
    # 3. 核心：利用 argsort 两次排序获取秩 (Rank)
    # axis=0 表示在截面（股票维度）上排序
    # 第一次 argsort 得到排序后的索引
    # 第二次 argsort 得到原始位置对应的排名
    order = np.argsort(alpha, axis=0)
    # 创建一个和 alpha 形状一样的网格，用于辅助 argsort 还原
    grid = np.ogrid[:n_stocks, :n_dates]
    
    # 这里的技巧是：argsort 不能直接返回 Rank，
    # 我们需要通过 order 在 axis=0 上再次进行索引映射
    # 这等同于在 C 层面完成了每一列的排序逻辑
    ranks = np.empty_like(order, dtype=float)
    ranks[order, np.arange(n_dates)] = np.arange(n_stocks)[:, None]
    
    # 4. 归一化处理
    # 由于存在 NaN，每列的有效股票数量不同
    # 我们需要计算每列(每天)的有效计数
    valid_counts = np.sum(mask, axis=0)
    
    # 处理不同日期的 Rank 归一化 (减去该列最小秩，除以有效跨度)
    # 先把 NaN 位置的 Rank 设为极小值，方便统一处理
    # 重新计算基于有效值的 Rank
    # 注意：这里为了严谨处理 NaN，我们需要对每一列的有效值重新对齐
    # 下面是一种更健壮的向量化对齐方式：
    
    # 找到每列中有效值的相对排名
    # 将 NaN 替换为无穷大，使其排在最后
    temp_alpha = np.where(mask, alpha, np.inf)
    order = np.argsort(temp_alpha, axis=0)
    
    # 构造还原索引
    row_indices = np.arange(n_stocks)[:, None]
    col_indices = np.arange(n_dates)
    
    final_ranks = np.empty((n_stocks, n_dates))
    final_ranks[order, col_indices] = row_indices
    
    # 5. 最终映射：(Rank) / (Count - 1)
    # 减去 1 是为了让排名范围在 [0, 1]
    res = final_ranks / (valid_counts - 1)
    
    # 恢复 NaN
    return np.where(mask, res, np.nan)




def cs_group_quantile(alpha, n_per_group):
    """
    截面分组算子 (每组固定人数版)
    :param alpha: np.ndarray (Stock, Date), 因子矩阵
    :param n_per_group: int, 每组期望的股票数量
    :return: np.ndarray (Stock, Date), 组号矩阵 (0 为最小组, 1 为次小组...)
    """
    n_stocks, n_dates = alpha.shape
    group_matrix = np.full_like(alpha, np.nan)
    
    # 1. 获取截面排名 (利用之前写的向量化排序逻辑)
    # 处理 NaN，确保它们排在最后或不参与分组
    mask = ~np.isnan(alpha)
    valid_counts = np.sum(mask, axis=0) # 每天有效股票数
    
    # 使用 argsort 获取排名
    temp_alpha = np.where(mask, alpha, np.inf)
    order = np.argsort(temp_alpha, axis=0)
    
    # 构造还原索引得到 Rank (0 到 n_stocks-1)
    ranks = np.empty((n_stocks, n_dates))
    ranks[order, np.arange(n_dates)] = np.arange(n_stocks)[:, None]
    
    # 2. 计算组号
    # 核心逻辑：组号 = 排名 // 每组人数
    # 注意：这里我们只对有效数据进行计算
    res_groups = ranks // n_per_group
    
    # 3. 处理溢出情况
    # 如果总数不能被 n_per_group 整除，最后一组的人数会少于 x
    # 如果你希望最后一组和倒数第二组合并，可以加逻辑，这里采用标准整除
    
    # 恢复 NaN 掩码
    group_matrix = np.where(mask, res_groups, np.nan)
    
    return group_matrix

