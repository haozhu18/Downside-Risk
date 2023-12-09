import pandas as pd
from tqdm import tqdm


_DATA_DIR = '../Data'
_STRATEGY_DIR = '../Strategy'
_STRATEGY_NAME = 'ETF'


def ols(Y, x):
    '''
    Given Y, estimate each column's beta with x
    '''
    
    covariance = (Y - Y.mean()).T @ (x - x.mean()) / (Y.shape[0] - 1)
    variance = x.var()
    
    return covariance / variance


def get_signal(df, group_name):
    '''
    Given a year of data, estimate the assets' beta's and downside beta's
    '''
    
    # Using the average market returns of the year as the threshold
    mkt = df[['mktrf', 'ldate']].groupby('ldate').first()
    threshold = mkt.mean()[0]
    down_idx = mkt[mkt['mktrf'] < threshold].index
    
    # Only consider assets with no missing returns for the year
    n_trading_days = len(mkt)
    df = df.loc[df.groupby(group_name)['excess_ret'].transform('count') == n_trading_days, :]
    
    # Compute beta and downside beta
    df_wide = df.pivot(columns=group_name, index='ldate', values='excess_ret')
    beta = ols(df_wide, mkt)
    
    df_down = df_wide.loc[down_idx, :]
    mkt_down = mkt.loc[down_idx, :]
    beta_down = ols(df_down, mkt_down)
    
    signal = (beta_down - beta).reset_index(names=group_name)
    signal = signal.rename(columns={'mktrf': 'signal'})
    signal['ldate'] = mkt.index[-1]
    
    return signal

 
if __name__ == '__main__':
    # Load Data
    if _STRATEGY_NAME == 'Equity':
        df = pd.read_parquet(f'{_DATA_DIR}/daily_data.parquet')
        group_name = 'permno'
    elif _STRATEGY_NAME == 'Bonds':
        df = pd.read_parquet(f'{_DATA_DIR}/bond_data.parquet')
        group_name = 'cusip'
    elif _STRATEGY_NAME == 'ETF':
        df = pd.read_parquet(f'{_DATA_DIR}/ETFdata.parquet')
        df.sort_values(by=['date', 'ticker'], inplace=True)
        df.rename(columns={'retd': 'daret', 'date': 'ldate'}, inplace=True)
        group_name = 'ticker'
    
    df.dropna(subset=['daret'])
    df['excess_ret'] = df['daret'] - df['rf']
    df = df[df['excess_ret'] > -1]
    
    # Prepare rolling windows
    start_date = df['ldate'].iloc[0]
    end_date = df['ldate'].iloc[-1]

    date_ranges = pd.date_range(start=start_date, end=end_date - pd.DateOffset(months=10), freq='M').to_period('M')

    windows = [(str(date), str(date + 12)) for date in date_ranges]

    # Calculate signals
    signals_rolling = []

    for window_start, window_end in tqdm(windows):
        df_year = df[(df['ldate'] > window_start) & (df['ldate'] < window_end)]
        signals_rolling.append(get_signal(df_year, group_name))

    signals_rolling = pd.concat(signals_rolling)

    # Reformat date to first of each month for future merging
    signals_rolling['ldate'] = signals_rolling['ldate'].values.astype('datetime64[M]')

    # Save the signals
    signals_rolling.to_parquet(f'{_STRATEGY_DIR}/signals_{_STRATEGY_NAME}.parquet')



