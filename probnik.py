import yfinance as yf 
test = yf.download("SBER.ME", start = "2015-01-01",end = "2026-01-01", progress=False)
print(test.tail())