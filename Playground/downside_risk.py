import qpm
import pandas as pd
import numpy as np
from tqdm import tqdm

_DATA_DIR = '../Data'

_SAMPLE_START = '2001-01-01'
_SAMPLE_END = '2023-12-31'
_REMOVE_MICRO_CAPS = True
_NUM_PORT = 5
_WINDOW_SIZE = 12

df = qpm.load_data(data_dir = _DATA_DIR, file_name = 'MasterData.parquet')
df['excess_ret'] = df['retx'] - df['rf']
df.head()


mkt = df[['mktrf', 'ldate']].groupby('ldate').first()
threshold = mkt.rolling(_WINDOW_SIZE).mean()
mkt['Down'] = np.where(mkt < threshold, 1, 0)
mkt.head()

def get_signal(excess_ret, mkt, window_size=_WINDOW_SIZE):
    """
    Given the excess returns of an asset and the excess market returns labeled with whether the market is down, return the signals.
    Note: this is filter by market down first, then run regression with fixed rolling window size 
    """
    
    asset_id = excess_ret.columns[0]
    df_aligned = excess_ret.join(mkt)
    df_aligned[[asset_id, 'mktrf']] = np.log(1 + df_aligned[[asset_id, 'mktrf']])
    df_down = df_aligned[df_aligned['Down']==1]
    #df_up = df_aligned[df_aligned['Down']==0]
    beta = df_aligned[asset_id].rolling(window_size).cov(df_aligned['mktrf']) / df_aligned['mktrf'].rolling(window_size).var()
    beta_down = df_down[asset_id].rolling(window_size).cov(df_down['mktrf']) / df_down['mktrf'].rolling(window_size).var()
    #beta_up = df_up[asset_id].rolling(window_size).cov(df_up['mktrf']) / df_up['mktrf'].rolling(window_size).var()
    signal = (beta_down - beta).ffill()
    
    return signal

for permno in tqdm(df['permno'].unique()):
    excess_ret = df.loc[df['permno']==permno, ['excess_ret', 'ldate']].set_index('ldate').rename(columns={"excess_ret": permno})
    df.loc[df['permno']==permno, 'signal'] = get_signal(excess_ret, mkt).values


#df['signal'] = qpm.create_lag(df, var_name='signal', lag=1)
#df.loc[df['ldate'].isin(mkt[mkt['Down']==1].index), 'signal'] = np.nan
df_select = qpm.select_sample(df, sample_start = _SAMPLE_START, sample_end = _SAMPLE_END, remove_micro_caps = _REMOVE_MICRO_CAPS)

df_select, df_rets = qpm.create_portfolios(df_select, sort_frequency = 'Monthly', num_port = _NUM_PORT)
#print(df_rets.tail())

qpm.analyze_strategy(df_rets, analysis_type = 'Performance')

#qpm.analyze_strategy(df_rets, analysis_type = 'Summary')

#qpm.analyze_strategy(df_rets, analysis_type = 'Factor Regression')