import shlex
import sys
import asyncio
import requests
from datetime import datetime
import jdatetime
import math


def convert_timestamp_to_jdate(timestamp):
    # Convert the timestamp to a Python datetime object
    datetime_obj = jdatetime.datetime.fromtimestamp(timestamp)
    return [str(datetime_obj.date()), datetime_obj.time()]


async def get_prices(symbol):
    url = f"https://api.nobitex.ir/v2/orderbook/{symbol}"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Check for any errors in the response
        data = response.json()
        return data
    except Exception as e:
        print(f"Error occurred: {e}")
        return []


async def get_usdt_price():
    usdt_data = await get_prices("USDTIRT")
    [last_transaction_date, last_transaction_time] = convert_timestamp_to_jdate(
        usdt_data['lastUpdate']/1000)
    print(
        f"symbol: USDT - IRT | {last_transaction_date} | {last_transaction_time}")
    print(f"price: {usdt_data['lastTradePrice']}")
    bids = usdt_data['bids'][:3]
    print(f"bids: {bids}")
    asks = usdt_data['asks'][:3]
    print(f"asks: {asks}")
    return {"price": usdt_data['lastTradePrice'], "bids": bids, "asks": asks}


async def get_coins_prices(symbol_name):
    coin_usdt_data = await get_prices(symbol_name+"USDT")
    [last_usdt_transaction_date, last_usdt_transaction_time] = convert_timestamp_to_jdate(
        coin_usdt_data['lastUpdate']/1000)
    usdt_bids = coin_usdt_data['bids'][:3]
    usdt_asks = coin_usdt_data['asks'][:3]
    coin_irt_data = await get_prices(symbol_name+"IRT")
    [last_irt_transaction_date, last_irt_transaction_time] = convert_timestamp_to_jdate(
        coin_irt_data['lastUpdate']/1000)
    irt_bids = coin_irt_data['bids'][:3]
    irt_asks = coin_irt_data['asks'][:3]
    return {"usdt_price": coin_usdt_data['lastTradePrice'], "usdt_bids": usdt_bids, "usdt_asks": usdt_asks,
            "usdt_last_date": f"{last_usdt_transaction_date} | {last_usdt_transaction_time}",
            "irt_price": coin_irt_data['lastTradePrice'], "irt_bids": irt_bids, "irt_asks": irt_asks,
            "irt_last_date": f"{last_irt_transaction_date} | {last_irt_transaction_time}"}


async def compare_prices(symbol_name, usdt_prices, coins_prices):
    if coins_prices['usdt_price']:
        print(f"-=-=-=-=-=-=-=-=-=-")
        print(f"symbol: {symbol_name} - USDT | {coins_prices['usdt_last_date']}")
        print(f"price: {coins_prices['usdt_price']}")
        bids = []
        for bid in coins_prices['usdt_bids']: bids.append(bid[0])
        print(f"bids: {bids}")
        asks = []
        for ask in coins_prices['usdt_asks']: asks.append(ask[0])
        print(f"asks: {asks}")
        print(f"-=-=-=-=-")
        print(f"symbol: {symbol_name} - IRT | {coins_prices['irt_last_date']}")
        print(f"price: {coins_prices['irt_price']} ==> {math.floor(float(coins_prices['irt_price'])/float(usdt_prices['price']))}")
        bids = []
        for bid in coins_prices['irt_bids']: bids.append(bid[0])
        converted_bids = []
        for bid in coins_prices['irt_bids']: converted_bids.append(math.floor(float(bid[0])/float(usdt_prices['price'])))
        print(f"bids: {bids} ==> {converted_bids}")
        asks = []
        for ask in coins_prices['irt_asks']: asks.append(ask[0])
        converted_asks = []
        for ask in coins_prices['irt_asks']: converted_asks.append(math.floor(float(ask[0])/float(usdt_prices['price'])))
        print(f"asks: {asks} ==> {converted_asks}")
        print(f"-=-=-=-=-")
        return math.floor(float(coins_prices['usdt_price'])) - math.floor(float(coins_prices['irt_price'])/float(usdt_prices['price']))
    else:
        return 0


async def main() -> int:
    print("_______________________________________________________________________________\n")
    symbols = ['BTCIRT', 'BTCUSDT', 'ETHIRT', 'ETHUSDT', 'LTCIRT', 'LTCUSDT', 'XRPIRT', 'XRPUSDT', 'BCHIRT', 'BCHUSDT', 'BNBIRT', 'BNBUSDT', 'EOSIRT', 'EOSUSDT', 'DOGEIRT', 'DOGEUSDT', 'XLMIRT', 'XLMUSDT', 'TRXIRT', 'TRXUSDT', 'ADAIRT', 'ADAUSDT', 'XMRIRT', 'XMRUSDT', 'ETCIRT', 'ETCUSDT', 'XTZIRT', 'XTZUSDT', 'LINKIRT', 'LINKUSDT', 'DAIIRT', 'DAIUSDT', 'DOTIRT', 'DOTUSDT', 'UNIIRT', 'UNIUSDT', 'AAVEIRT', 'AAVEUSDT', 'SOLIRT', 'SOLUSDT', 'MATICIRT', 'MATICUSDT', 'FILIRT', 'FILUSDT', 'GRTIRT', 'GRTUSDT', 'SHIBIRT', 'SHIBUSDT', '1INCHIRT', '1INCHUSDT', 'ATOMIRT', 'ATOMUSDT', 'AVAXIRT', 'AVAXUSDT', 'AXSIRT', 'AXSUSDT', 'BALIRT', 'BALUSDT', 'BANDIRT', 'BANDUSDT', 'BATIRT', 'BATUSDT', '1M_BTTIRT', '1M_BTTUSDT', 'CELRIRT', 'CELRUSDT', 'COMPIRT', 'COMPUSDT', 'EGLDIRT', 'EGLDUSDT', 'FTMIRT', 'FTMUSDT', 'GALAIRT', 'GALAUSDT', 'MASKIRT', 'MASKUSDT', 'MKRIRT', 'MKRUSDT', 'NEARIRT', 'NEARUSDT', 'SNXIRT', 'SNXUSDT', 'SUSHIIRT', 'SUSHIUSDT', 'YFIIRT', 'YFIUSDT', 'MANAIRT', 'MANAUSDT', 'SANDIRT', 'SANDUSDT', 'APEIRT', 'APEUSDT', 'ONEIRT', 'ONEUSDT', 'WBTCIRT', 'WBTCUSDT', 'USDCIRT', 'USDCUSDT', 'ALGOIRT', 'ALGOUSDT', 'GMTIRT', 'GMTUSDT', 'CHZIRT', 'CHZUSDT', 'QNTIRT', 'QNTUSDT', 'BUSDIRT', 'BUSDUSDT', 'FLOWIRT', 'FLOWUSDT', 'HBARIRT', 'HBARUSDT', 'EGALAIRT', 'EGALAUSDT', 'ENJIRT', 'ENJUSDT', 'CRVIRT', 'CRVUSDT', 'LDOIRT', 'LDOUSDT', 'DYDXIRT', 'DYDXUSDT', 'APTIRT', 'APTUSDT', 'FLRIRT', 'FLRUSDT', 'LRCIRT', 'LRCUSDT', 'ENSIRT', 'ENSUSDT', 'LPTIRT', 'LPTUSDT', 'GLMIRT', 'GLMUSDT', 'API3IRT', 'API3USDT', 'DAOIRT', 'DAOUSDT', 'CVCIRT', 'CVCUSDT', 'NMRIRT', 'NMRUSDT', 'STORJIRT', 'STORJUSDT', 'CVXIRT', 'CVXUSDT', 'SNTIRT', 'SNTUSDT', 'SLPIRT', 'SLPUSDT', '1M_NFTIRT', '1M_NFTUSDT', 'ANTIRT', 'ANTUSDT', 'ILVIRT', 'ILVUSDT', 'TIRT', 'TUSDT', '1B_BABYDOGEIRT', '1B_BABYDOGEUSDT', 'TONIRT', 'TONUSDT', '100K_FLOKIIRT', '100K_FLOKIUSDT', 'ZRXIRT', 'ZRXUSDT', 'IMXIRT', 'IMXUSDT', 'MDTIRT', 'MDTUSDT', 'BLURIRT', 'BLURUSDT', 'MAGICIRT', 'MAGICUSDT', 'ARBIRT', 'ARBUSDT', 'GMXIRT', 'GMXUSDT', 'SSVIRT', 'SSVUSDT', 'WLDIRT', 'WLDUSDT', 'OMGIRT', 'OMGUSDT', 'RDNTIRT', 'RDNTUSDT', 'JSTIRT', 'JSTUSDT', 'RNDRIRT', 'RNDRUSDT']
    symbols = ['BTCIRT', 'BTCUSDT', 'ETHIRT', 'ETHUSDT', 'LTCIRT', 'LTCUSDT', 'BNBIRT', 'BNBUSDT', 'DOGEIRT', 'DOGEUSDT', 'XLMIRT', 'XLMUSDT', 'TRXIRT', 'TRXUSDT', 'ADAIRT', 'ADAUSDT']
    usdt_prices = await get_usdt_price()
    result_list = {}
    for symbol in symbols:
        # get btc prices in irt and usdt
        # compare prices and see the diffrences in irt and usdt
        if "USDT" in symbol:
            symbol_name = symbol.split("USDT")[0]
        elif "IRT" in symbol:
            continue
        coins_prices = await get_coins_prices(symbol_name)
        result = await compare_prices(symbol_name, usdt_prices, coins_prices)
        print(result)
        result_list[symbol_name] = result
    print(f"-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print(f"-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-")
    print(result_list)

if __name__ == '__main__':
    asyncio.run(main())
