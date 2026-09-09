import pandas as pd
from datetime import date 
from riskcore.data.integrity import data_integrity_report 
from riskcore.data.universe import tickers 
from riskcore.data.integrity import detect_anomalies
from riskcore.data.loader import load_universe_history, today
prices = load_universe_history(tickers,"2015-01-01", today ) 
def print_ticker_all(prices, ticker):
    print(f'*****Данные по {ticker}*****')
    print(prices[ticker])
    

    
    
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