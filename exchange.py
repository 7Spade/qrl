import ccxt

def get_exchange():
    exchange = ccxt.mexc({
        "apiKey": os.getenv("MEXC_API_KEY"),
        "secret": os.getenv("MEXC_API_SECRET"),
        "enableRateLimit": True,
    })
    return exchange
