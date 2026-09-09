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
    df = pd.DataFrame(all_rows,columns=data["history"]["columns"])
    return df
def load_universe_history(tickers,date_from,date_till):
    return {t: get_cached_history(t,date_from,date_till) for t in tickers}