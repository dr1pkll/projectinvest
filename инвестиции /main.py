from pandas.core.arrays import period
from pandas.core.dtypes.cast import na_value_for_dtype
import requests
import pandas as pd
import os
from datetime import date 
today = date.today().strftime("%Y-%m-%d")
def cache_path(ticker, cache_dir="data/cache"):
    return f"{cache_dir}/{ticker}.parquet"
def get_cached_history(ticker, date_from, date_till,cache_dir="data/cache"):
    os.makedirs(cache_dir, exist_ok=True)
    path = cache_path(ticker, cache_dir)
    if not os.path.exists(path):
        df = get_moex_history(ticker, date_from, date_till)
        df = df[["TRADEDATE",'HIGH','LOW','VOLUME','CLOSE']].set_index("TRADEDATE")
        df.index = pd.to_datetime(df.index)
        df.to_parquet(path)
        return df 
    else:
        cached = pd.read_parquet(path)
        last_date = cached.index.max()  
        if last_date >= pd.Timestamp(date_till):
            return cached
        next_start = (last_date + pd.Timedelta(1)).strftime("%Y-%m-%d")
        new_date = get_moex_history(ticker, next_start, date_till)
        new_date = new_date[["TRADEDATE",'HIGH','LOW','VOLUME','CLOSE']].set_index("TRADEDATE")
        new_date.index = pd.to_datetime(new_date.index)
        combined= pd.concat([cached, new_date])
        combined = combined[~combined.index.duplicated(keep='last')]
        combined = combined.sort_index()
        combined.to_parquet(path)
    
        return combined

def get_moex_history(ticker,date_from,date_till ):
    url = f"https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
    all_rows = []
    start = 0

    while True:
        params = {"from": date_from, "till": date_till, "start": start}
        resp = requests.get(url, params=params)
        data = resp.json()
        rows = data["history"]["data"]
        if not rows:
            break
        all_rows.extend(rows)
        start += 100

    df = pd.DataFrame(all_rows, columns=data["history"]["columns"])
    return df
tickers = ['SBER', 'GAZP', 'LKOH', 'GMKN', 'ROSN', 'NVTK', 'MTSS', 'MGNT', 'YDEX', 'TATN', 'SNGS', 'CHMF', 'ALRS', 'PLZL', 'PHOR', 'RUAL', 'AFLT', 'IRAO', 'MOEX', 'VTBR']
prices = {}
for t in tickers: 
    prices[t] = get_cached_history(t, "2015-01-01", today)
close_series = {}
volume_series = {}
high_series = {}
low_series = {}
for t in prices:
    df = prices[t]
    close_series[t] = df["CLOSE"]
    volume_series[t] = df["VOLUME"]
    high_series[t]  = df["HIGH"]
    low_series[t] = df["LOW"]
close_prices = pd.DataFrame(close_series)
volume_prices   = pd.DataFrame(volume_series)
volume_prices.index = pd.to_datetime(volume_prices.index)
close_prices.index =  pd.to_datetime(close_prices.index)
high_prices = pd.DataFrame(high_series)
high_prices.index= pd.to_datetime(high_prices.index)
low_prices  = pd.DataFrame(low_series)
low_prices.index = pd.to_datetime(low_prices.index)
month_price = close_prices.resample("ME").last()
def data_integrity_report(df, ticker):
    report={}
    report["duplicated"] = df.index.duplicated().sum()
    diffs = df.index.to_series().diff()
    gaps_mask = diffs>=pd.Timedelta(days=4)
    g_date = diffs[gaps_mask]
    report["gaps"] ={"count":len(g_date), "dates":dict(zip(g_date.index.strftime("%Y-%m-%d"), g_date.dt.days))}
    zero_true = df["VOLUME"] == 0
    zero_mask = df["VOLUME"][zero_true]
    report["zero_volume"] ={"count":len(zero_mask), "dates":zero_mask.index.strftime("%Y-%m-%d").tolist()}
    return report
def detect_anomality(df,window=(1,5,20),percentile=0.99):
    returns = df["CLOSE"].pct_change(period = n)
    quantile_anomalies = returns.abs().quantile(0,99)
    outliers = returns[returns.abs()>quantile_anomalies]

print(close_prices.shape)
print(month_price.tail(10))
print(data_integrity_report(prices["SBER"], "SBER"))