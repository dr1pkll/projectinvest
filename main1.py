#import yfinance as yf 
import matplotlib.pyplot as plt 
import matplotlib.dates as mdates 
import requests
gold = yf.download("GC=F", start='2000-01-01', end  = '2026-01-01', progress= False)

plt.plot(gold.index, gold["Close"], label ="Ценя закрыти", color = "blue", linewidth = 2)
print(gold.head())
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator(base = 2))
plt.title("Динамика цен золота (2000-2026)", fontsize = 14 )
plt.xlabel("Год", fontsize = 12)
plt.ylabel("Цена за унцию (USD)")
plt.grid(True, linestyle =':', alpha = 0.7)
plt.legend()
plt.show()
print(gold.head())
gold["return"] = gold["Close"].pct_change() # precent change 
gold["valatililty20d"] = gold["return"].rolling(20).std()
plt.plot(gold.index, gold["valatililty20d"],  color = "red", linewidth = 1)
plt.title("Дневная волатильность золота", fontsize = 14)
plt.xlabel("Год", fontsize = 12)
plt.ylabel("Волатильность", fontsize=12)
plt.grid(False)
plt.show()
import requests
import pandas as pd
url = "https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/SBER.json"
start  = 0 
all_rows = []
while True: 
    params = {"from" : "2015-01-01", "till" : "2026-01-01"}
    response = requests.get(url, params=params)
    data = response.json()
    rows = data["history"]["data"]
    if not rows:
        break
df = pd.DataFrame(all_rows, columns=data["history"]["columns"])
print(df.shape)
print(df[["TRADEDATE","CLOSE"]]).tail()#