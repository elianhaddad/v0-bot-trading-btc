import pandas as pd
from binance.client import Client
import os
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

# Database imports
try:
    from src.database.models import PriceData
    from src.database.connection import get_db, init_db
    DATABASE_AVAILABLE = True
except ImportError:
    print("Database modules not available. Running in CSV-only mode.")
    DATABASE_AVAILABLE = False

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinanceDataCollector:
    def __init__(self, api_key: str, api_secret: str, use_database: bool = True):
        """
        Initialize Binance Data Collector
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            use_database: Whether to use database storage (default: True)
        """
        self.client = Client(api_key, api_secret)
        self.use_database = use_database and DATABASE_AVAILABLE
        
        if self.use_database:
            try:
                # Initialize database
                init_db()
                self.db = next(get_db())
                logger.info("Database connection established")
            except Exception as e:
                logger.error(f"Database initialization failed: {e}")
                self.use_database = False
                logger.info("Falling back to CSV-only mode")
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'db') and self.db:
            self.db.close()
    
    def get_binance_klines(self, symbol: str, interval: str, start_date: str, end_date: str) -> pd.DataFrame:
        """
        Fetch historical candle data from Binance and store in both CSV and database
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Kline interval (e.g., Client.KLINE_INTERVAL_1MINUTE)
            start_date: Start date string
            end_date: End date string
            
        Returns:
            pandas.DataFrame: OHLCV data
        """
        try:
            logger.info(f"Fetching {symbol} data from {start_date} to {end_date}")
            
            # Fetch historical candle data (OHLCV)
            candles = self.client.get_historical_klines(symbol, interval, start_date, end_date)
            
            if not candles:
                logger.warning("No candle data received from Binance")
                return pd.DataFrame()
            
            # Convert the data to a pandas DataFrame
            df = pd.DataFrame(candles, columns=[
                "open_time", "open", "high", "low", "close", "volume", "close_time",
                "quote_asset_volume", "number_of_trades", "taker_buy_volume",
                "taker_buy_quote_volume", "ignore"
            ])
            
            # Convert timestamp columns to readable dates
            df['open_time'] = pd.to_datetime(df['open_time'], unit='ms')
            df['close_time'] = pd.to_datetime(df['close_time'], unit='ms')
            
            # Convert price and volume columns to float
            price_volume_cols = ['open', 'high', 'low', 'close', 'volume', 'quote_asset_volume', 
                               'taker_buy_volume', 'taker_buy_quote_volume']
            df[price_volume_cols] = df[price_volume_cols].astype(float)
            
            # Drop unnecessary columns
            df.drop(columns=['ignore'], inplace=True)
            
            # Save to CSV (your original functionality)
            self._save_to_csv(df, symbol, interval)
            
            # Save to database if available
            if self.use_database:
                self._save_to_database(df, symbol, interval)
            
            logger.info(f"Successfully processed {len(df)} candles for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching Binance data: {e}")
            raise
    
    def _save_to_csv(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        """Save DataFrame to CSV file (original functionality)"""
        try:
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
            logger.info(f"Data saved to CSV: {csv_path}")
            
        except Exception as e:
            logger.error(f"Error saving to CSV: {e}")
    
    def _save_to_database(self, df: pd.DataFrame, symbol: str, interval: str) -> None:
        """Save DataFrame to PostgreSQL database"""
        try:
            saved_count = 0
            duplicate_count = 0
            
            for _, row in df.iterrows():
                try:
                    # Create PriceData object
                    price_data = PriceData(
                        timestamp=row['open_time'],
                        symbol=symbol,
                        open=row['open'],
                        high=row['high'],
                        low=row['low'],
                        close=row['close'],
                        volume=row['volume'],
                        timeframe=self._convert_interval_to_timeframe(interval)
                    )
                    
                    # Add to database
                    self.db.add(price_data)
                    self.db.commit()
                    saved_count += 1
                    
                except IntegrityError:
                    # Handle duplicate entries
                    self.db.rollback()
                    duplicate_count += 1
                except Exception as e:
                    self.db.rollback()
                    logger.error(f"Error saving individual record: {e}")
            
            logger.info(f"Database save complete: {saved_count} new records, {duplicate_count} duplicates skipped")
            
        except Exception as e:
            logger.error(f"Error saving to database: {e}")
    
    def _convert_interval_to_timeframe(self, interval: str) -> str:
        """Convert Binance interval to timeframe string"""
        interval_map = {
            Client.KLINE_INTERVAL_1MINUTE: '1m',
            Client.KLINE_INTERVAL_3MINUTE: '3m',
            Client.KLINE_INTERVAL_5MINUTE: '5m',
            Client.KLINE_INTERVAL_15MINUTE: '15m',
            Client.KLINE_INTERVAL_30MINUTE: '30m',
            Client.KLINE_INTERVAL_1HOUR: '1h',
            Client.KLINE_INTERVAL_2HOUR: '2h',
            Client.KLINE_INTERVAL_4HOUR: '4h',
            Client.KLINE_INTERVAL_6HOUR: '6h',
            Client.KLINE_INTERVAL_8HOUR: '8h',
            Client.KLINE_INTERVAL_12HOUR: '12h',
            Client.KLINE_INTERVAL_1DAY: '1d',
            Client.KLINE_INTERVAL_3DAY: '3d',
            Client.KLINE_INTERVAL_1WEEK: '1w',
            Client.KLINE_INTERVAL_1MONTH: '1M'
        }
        return interval_map.get(interval, '1m')
    
    def get_latest_data_from_db(self, symbol: str = 'BTCUSDT', timeframe: str = '1m', limit: int = 100) -> Optional[pd.DataFrame]:
        """
        Get latest data from database
        
        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe (e.g., '1m', '5m', '1h')
            limit: Number of records to fetch
            
        Returns:
            pandas.DataFrame or None: Latest price data
        """
        if not self.use_database:
            logger.warning("Database not available")
            return None
        
        try:
            # Query latest data from database
            price_data = self.db.query(PriceData)\
                .filter(PriceData.symbol == symbol)\
                .filter(PriceData.timeframe == timeframe)\
                .order_by(PriceData.timestamp.desc())\
                .limit(limit)\
                .all()
            
            if not price_data:
                logger.info(f"No data found in database for {symbol} {timeframe}")
                return None
            
            # Convert to DataFrame
            data = []
            for record in price_data:
                data.append({
                    'open_time': record.timestamp,
                    'open': record.open,
                    'high': record.high,
                    'low': record.low,
                    'close': record.close,
                    'volume': record.volume,
                    'symbol': record.symbol,
                    'timeframe': record.timeframe
                })
            
            df = pd.DataFrame(data)
            df = df.sort_values('open_time').reset_index(drop=True)
            
            logger.info(f"Retrieved {len(df)} records from database")
            return df
            
        except Exception as e:
            logger.error(f"Error retrieving data from database: {e}")
            return None
    
    def is_data_stale(self, symbol: str = 'BTCUSDT', timeframe: str = '1m', max_age_minutes: int = 5) -> bool:
        """
        Check if data in database is stale
        
        Args:
            symbol: Trading pair symbol
            timeframe: Timeframe to check
            max_age_minutes: Maximum age in minutes before data is considered stale
            
        Returns:
            bool: True if data is stale or doesn't exist
        """
        if not self.use_database:
            return True
        
        try:
            latest_record = self.db.query(PriceData)\
                .filter(PriceData.symbol == symbol)\
                .filter(PriceData.timeframe == timeframe)\
                .order_by(PriceData.timestamp.desc())\
                .first()
            
            if not latest_record:
                return True
            
            # Check if data is older than max_age_minutes
            time_diff = datetime.utcnow() - latest_record.timestamp
            return time_diff.total_seconds() > (max_age_minutes * 60)
            
        except Exception as e:
            logger.error(f"Error checking data staleness: {e}")
            return True

# Backward compatibility function (your original function)
def get_binance_klines(symbol, interval, start_date, end_date, api_key, api_secret):
    """
    Original function for backward compatibility
    """
    collector = BinanceDataCollector(api_key, api_secret)
    return collector.get_binance_klines(symbol, interval, start_date, end_date)

# Example usage with your original parameters
if __name__ == "__main__":
    # Your original API keys (consider moving these to environment variables)
    API_KEY = 'sqYxQ03ykXJ4fGjVEEFN80IvzpqzEnNUyJ2Jpjoo6ve8HgsdZLB4i5YLYjcx2hwJ'
    API_SECRET = '6HfXzlGSl33YuWr1FLaHhSFpermn6gKfbTm0ls4j7sdCsmetDMsBVGGTyrRY5Dt3'
    
    # Create collector instance
    collector = BinanceDataCollector(API_KEY, API_SECRET)
    
    # Fetch data (your original call)
    df = collector.get_binance_klines('BTCUSDT', Client.KLINE_INTERVAL_1MINUTE, '2025-01-01', '2025-01-07')
    print(f"Fetched {len(df)} records")
    print(df.head())
    
    # Check if data is stale
    if collector.is_data_stale('BTCUSDT', '1m'):
        print("Data is stale, consider fetching new data")
    else:
        print("Data is fresh")
    
    # Get latest data from database
    latest_df = collector.get_latest_data_from_db('BTCUSDT', '1m', 10)
    if latest_df is not None:
        print("\nLatest 10 records from database:")
        print(latest_df.tail())
