import aiohttp
import asyncio
import certifi
import ssl
import json
import sys
import platform
from datetime import datetime, timedelta

API_URL = 'https://api.privatbank.ua/p24api/exchange_rates?json&'
CURRENCIES = {"EUR", "USD"}
MAX_DAYS = 10

async def get_data(date):
    url = f"{API_URL}date={date}"
    try:
        async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=ssl.create_default_context(cafile=certifi.where()))) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    result = {}
                    for key in data.get('exchangeRate', []):
                        currency = key.get('currency')
                        if currency in CURRENCIES:
                            result[currency] = {
                                'sale': key.get('saleRate'),
                                'purchase': key.get('purchaseRate'),
                            }
                    return {data.get('date', 'unknown'): result}
                else:
                    return f"Error: Failed to fetch data, status: {response.status}"
    except Exception as err:
        return f"ERROR: {err}"

async def main(index_days):
    if int(index_days) > MAX_DAYS or int(index_days) < 0:
        return "Invalid number of days. Please enter a number between 0 and 10."

    now = datetime.now()
    dates = [(now - timedelta(days=int(i))).strftime("%d.%m.%Y") for i in range(int(index_days))]

    task = [get_data(date) for date in dates]
    result = await asyncio.gather(*task)
    return result


if __name__ == "__main__":
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    r = asyncio.run(main(sys.argv[1]))
    print(json.dumps(r, indent=4, ensure_ascii=False))
