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
def detect_anomalies(df, return_periods=(1, 5, 20), lookback=250, percentile=0.99):
    anomalies = {}
    for period in return_periods:
        returns =df["CLOSE"].pct_change(periods = period)
        return_abs = returns.abs()
        threshold = return_abs.rolling(window = lookback, min_periods =lookback).quantile(percentile).shift(1)
        is_outlier = return_abs > threshold
        outlier = returns[is_outlier]
        anomalies[period]={
            "count":len(outlier),
            "dates":outlier.index.strftime("%Y-%m-%d").tolist(),
            "values":outlier.values.tolist()
        }
    return anomalies

def print_integrity_report(report, ticker):
    print(f"\n******* Интегральная проверка данных для {ticker} ******")
    print(f"Данные содержат {report['duplicated']} дубликатов")
    gaps = report["gaps"]
    print(f"Разрывы в календаре: {gaps['count']}")
    if gaps['count']:
        gaps_df = pd.DataFrame(list(gaps["dates"].items()),columns=["Дата", "Разрыв (дней)"])
        print(gaps_df.to_string(index=False))
    zv = report['zero_volume']
    print(f'\n Нулевой объем торгов {zv["count"]}')
    if zv['count']:
        print(pd.DataFrame({"Дата": zv['dates']}).to_string(index=False))

def print_anomalies_report(anomalies, ticker):
    print(f"\n===== Аномальные доходности: {ticker} =====")
    for period, data in anomalies.items():
        print(f"\n--- Период {period} дн. торгов (найдено: {data['count']}) ---")
        if data["count"]:
            df = pd.DataFrame({"Дата": data["dates"], "Доходность": data["values"]})
            df["Доходность"] = (df["Доходность"] * 100).round(2).astype(str) + "%"
            print(df.to_string(index=False))
for t in tickers:
        
    integrity = data_integrity_report(prices[t],t )
    print_integrity_report(integrity, t)

    anomalies = detect_anomalies(prices[t])
    print_anomalies_report(anomalies, t)