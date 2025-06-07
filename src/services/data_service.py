import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from src.database.repository import Repository
from src.database.connection import get_db

logger = logging.getLogger(__name__)

class DataService:
    def __init__(self, db: Optional[Session] = None):
        """Initialize data service with database session"""
        if db:
            self.db = db
            self.repository = Repository(db)
            self.close_db = False
        else:
            self.db = next(get_db())
            self.repository = Repository(self.db)
            self.close_db = True
    
    def __del__(self):
        """Close database connection if needed"""
        if hasattr(self, 'close_db') and self.close_db and hasattr(self, 'db'):
            self.db.close()
    
    def store_candle_data(self, candle_data: Dict[str, Any]) -> bool:
        """Store single candle data in database"""
        try:
            # Format data for database
            db_data = {
                'timestamp': datetime.fromtimestamp(candle_data['timestamp'] / 1000) 
                    if isinstance(candle_data['timestamp'], int) 
                    else candle_data['timestamp'],
                'symbol': candle_data.get('symbol', 'BTC/USDT'),
                'open': float(candle_data['open']),
                'high': float(candle_data['high']),
                'low': float(candle_data['low']),
                'close': float(candle_data['close']),
                'volume': float(candle_data['volume']),
                'timeframe': candle_data.get('timeframe', '1m')
            }
            
            self.repository.save_price_data(db_data)
            return True
        except Exception as e:
            logger.error(f"Error storing candle data: {e}")
            return False
    
    def store_candle_batch(self, candles: List[Dict[str, Any]]) -> bool:
        """Store multiple candles in database"""
        try:
            # Format data for database
            db_data_list = []
            for candle in candles:
                db_data = {
                    'timestamp': datetime.fromtimestamp(candle['timestamp'] / 1000) 
                        if isinstance(candle['timestamp'], int) 
                        else candle['timestamp'],
                    'symbol': candle.get('symbol', 'BTC/USDT'),
                    'open': float(candle['open']),
                    'high': float(candle['high']),
                    'low': float(candle['low']),
                    'close': float(candle['close']),
                    'volume': float(candle['volume']),
                    'timeframe': candle.get('timeframe', '1m')
                }
                db_data_list.append(db_data)
            
            self.repository.save_price_data_batch(db_data_list)
            return True
        except Exception as e:
            logger.error(f"Error storing candle batch: {e}")
            return False
    
    def store_technical_indicators(self, indicators: Dict[str, Any], timestamp: Optional[datetime] = None) -> bool:
        """Store technical indicators in database"""
        try:
            # Format data for database
            db_data = {
                'timestamp': timestamp or datetime.utcnow(),
                'symbol': indicators.get('symbol', 'BTC/USDT'),
                'rsi': indicators.get('rsi'),
                'macd': indicators.get('macd', {}).get('macd'),
                'macd_signal': indicators.get('macd', {}).get('signal'),
                'macd_histogram': indicators.get('macd', {}).get('histogram'),
                'bb_upper': indicators.get('bollinger_bands', {}).get('upper'),
                'bb_middle': indicators.get('bollinger_bands', {}).get('middle'),
                'bb_lower': indicators.get('bollinger_bands', {}).get('lower'),
                'ema_20': indicators.get('ema_20'),
                'ema_50': indicators.get('ema_50'),
                'sma_200': indicators.get('sma_200')
            }
            
            self.repository.save_technical_indicator(db_data)
            return True
        except Exception as e:
            logger.error(f"Error storing technical indicators: {e}")
            return False
    
    def store_trading_signal(self, signal: Dict[str, Any]) -> bool:
        """Store trading signal in database"""
        try:
            # Format data for database
            db_data = {
                'timestamp': signal.get('timestamp', datetime.utcnow()),
                'symbol': signal.get('symbol', 'BTC/USDT'),
                'signal_type': signal.get('signal'),
                'confidence': signal.get('confidence'),
                'price': signal.get('price'),
                'reasoning': signal.get('reasoning'),
                'ai_analysis': signal
            }
            
            self.repository.save_trading_signal(db_data)
            return True
        except Exception as e:
            logger.error(f"Error storing trading signal: {e}")
            return False
    
    def get_latest_price(self, symbol: str = 'BTC/USDT', timeframe: str = '1m') -> Optional[Dict[str, Any]]:
        """Get latest price data for symbol and timeframe"""
        try:
            price_data = self.repository.get_latest_price_data(symbol, timeframe)
            if not price_data:
                return None
            
            return {
                'timestamp': price_data.timestamp,
                'symbol': price_data.symbol,
                'open': price_data.open,
                'high': price_data.high,
                'low': price_data.low,
                'close': price_data.close,
                'volume': price_data.volume,
                'timeframe': price_data.timeframe
            }
        except Exception as e:
            logger.error(f"Error getting latest price: {e}")
            return None
    
    def get_historical_prices(self, 
                             symbol: str = 'BTC/USDT', 
                             timeframe: str = '1m',
                             limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical price data"""
        try:
            price_data_list = self.repository.get_price_data(symbol, timeframe, limit)
            
            return [{
                'timestamp': data.timestamp,
                'symbol': data.symbol,
                'open': data.open,
                'high': data.high,
                'low': data.low,
                'close': data.close,
                'volume': data.volume,
                'timeframe': data.timeframe
            } for data in price_data_list]
        except Exception as e:
            logger.error(f"Error getting historical prices: {e}")
            return []
    
    def is_data_stale(self, symbol: str = 'BTC/USDT', timeframe: str = '1m', max_age_seconds: int = 60) -> bool:
        """Check if data is stale"""
        try:
            latest_price = self.get_latest_price(symbol, timeframe)
            if not latest_price:
                return True
            
            age = (datetime.utcnow() - latest_price['timestamp']).total_seconds()
            return age > max_age_seconds
        except Exception as e:
            logger.error(f"Error checking if data is stale: {e}")
            return True
    
    def log_system_message(self, level: str, message: str, data: Any = None) -> bool:
        """Log system message to database"""
        try:
            self.repository.log_message(level, message, data)
            return True
        except Exception as e:
            logger.error(f"Error logging system message: {e}")
            return False
