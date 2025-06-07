import pandas as pd
from binance.client import Client
import os

def get_binance_klines(symbol, interval, start_date, end_date, api_key, api_secret):
    client = Client(api_key, api_secret)

    # Fetch historical candle data (OHLCV)
    candles = client.get_historical_klines(symbol, interval, start_date, end_date)

    # Convert the data to a pandas DataFrame
    df = pd.DataFrame(candles, columns=[
        "open_time", "open", "high", "low", "close", "volume", "close_time",
        "quote_asset_volume", "number_of_trades", "taker_buy_volume",
        "taker_buy_quote_volume", "ignore"
    ])

    # Convert timestamp columns to readable dates
    df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
    df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')

    # Drop unnecessary columns
    df.drop(columns=['ignore'], inplace=True)

    # Define CSV file path
    csv_dir = "data"
    csv_path = os.path.join(csv_dir, f"{symbol}_{interval}.csv")

    # Create the data directory if it doesn't exist
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)

    # If CSV exists, append only new data (avoid duplicates)
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        existing_df['open_time'] = pd.to_datetime(existing_df['open_time'])

        # Concatenate and drop duplicates
        df = pd.concat([existing_df, df]).drop_duplicates(subset=['open_time']).sort_values(by='open_time')

    # Save DataFrame to CSV
    df.to_csv(csv_path, index=False)

    return df

# Example usage
df = get_binance_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, '2025-01-01', '2024-04-06', 'sqYxQ03ykXJ4fGjVEEFN80IvzpqzEnNUyJ2Jpjoo6ve8HgsdZLB4i5YLYjcx2hwJ', '6HfXzlGSl33YuWr1FLaHhSFpermn6gKfbTm0ls4j7sdCsmetDMsBVGGTyrRY5Dt3')
print(df.head())