import pandas as pd
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
