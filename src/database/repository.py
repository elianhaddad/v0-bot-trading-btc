from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import json
import logging
from src.database.models import PriceData, TechnicalIndicator, TradingSignal, BotConfig, SystemLog

logger = logging.getLogger(__name__)

class Repository:
    def __init__(self, db: Session):
        self.db = db
    
    # Price Data methods
    def save_price_data(self, data: Dict[str, Any]) -> PriceData:
        """Save price data to database"""
        try:
            price_data = PriceData(
                timestamp=data.get('timestamp'),
                symbol=data.get('symbol', 'BTC/USDT'),
                open=data.get('open'),
                high=data.get('high'),
                low=data.get('low'),
                close=data.get('close'),
                volume=data.get('volume'),
                timeframe=data.get('timeframe', '1m')
            )
            
            self.db.add(price_data)
            self.db.commit()
            self.db.refresh(price_data)
            return price_data
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving price data: {e}")
            raise
    
    def save_price_data_batch(self, data_list: List[Dict[str, Any]]) -> List[PriceData]:
        """Save multiple price data records in batch"""
        try:
            price_data_objects = []
            for data in data_list:
                price_data = PriceData(
                    timestamp=data.get('timestamp'),
                    symbol=data.get('symbol', 'BTC/USDT'),
                    open=data.get('open'),
                    high=data.get('high'),
                    low=data.get('low'),
                    close=data.get('close'),
                    volume=data.get('volume'),
                    timeframe=data.get('timeframe', '1m')
                )
                price_data_objects.append(price_data)
            
            self.db.add_all(price_data_objects)
            self.db.commit()
            return price_data_objects
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving batch price data: {e}")
            raise
    
    def get_latest_price_data(self, symbol: str = 'BTC/USDT', timeframe: str = '1m') -> Optional[PriceData]:
        """Get latest price data for symbol and timeframe"""
        try:
            return self.db.query(PriceData)\
                .filter(PriceData.symbol == symbol)\
                .filter(PriceData.timeframe == timeframe)\
                .order_by(PriceData.timestamp.desc())\
                .first()
        except Exception as e:
            logger.error(f"Error getting latest price data: {e}")
            raise
    
    def get_price_data(self, 
                      symbol: str = 'BTC/USDT', 
                      timeframe: str = '1m',
                      limit: int = 100,
                      start_time: Optional[datetime] = None,
                      end_time: Optional[datetime] = None) -> List[PriceData]:
        """Get price data with filters"""
        try:
            query = self.db.query(PriceData)\
                .filter(PriceData.symbol == symbol)\
                .filter(PriceData.timeframe == timeframe)
            
            if start_time:
                query = query.filter(PriceData.timestamp >= start_time)
            
            if end_time:
                query = query.filter(PriceData.timestamp <= end_time)
            
            return query.order_by(PriceData.timestamp.desc()).limit(limit).all()
        except Exception as e:
            logger.error(f"Error getting price data: {e}")
            raise
    
    # Technical Indicators methods
    def save_technical_indicator(self, data: Dict[str, Any]) -> TechnicalIndicator:
        """Save technical indicator to database"""
        try:
            indicator = TechnicalIndicator(
                timestamp=data.get('timestamp'),
                symbol=data.get('symbol', 'BTC/USDT'),
                rsi=data.get('rsi'),
                macd=data.get('macd'),
                macd_signal=data.get('macd_signal'),
                macd_histogram=data.get('macd_histogram'),
                bb_upper=data.get('bb_upper'),
                bb_middle=data.get('bb_middle'),
                bb_lower=data.get('bb_lower'),
                ema_20=data.get('ema_20'),
                ema_50=data.get('ema_50'),
                sma_200=data.get('sma_200')
            )
            
            self.db.add(indicator)
            self.db.commit()
            self.db.refresh(indicator)
            return indicator
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving technical indicator: {e}")
            raise
    
    def get_latest_technical_indicator(self, symbol: str = 'BTC/USDT') -> Optional[TechnicalIndicator]:
        """Get latest technical indicator for symbol"""
        try:
            return self.db.query(TechnicalIndicator)\
                .filter(TechnicalIndicator.symbol == symbol)\
                .order_by(TechnicalIndicator.timestamp.desc())\
                .first()
        except Exception as e:
            logger.error(f"Error getting latest technical indicator: {e}")
            raise
    
    # Trading Signal methods
    def save_trading_signal(self, data: Dict[str, Any]) -> TradingSignal:
        """Save trading signal to database"""
        try:
            signal = TradingSignal(
                timestamp=data.get('timestamp', datetime.utcnow()),
                symbol=data.get('symbol', 'BTC/USDT'),
                signal_type=data.get('signal_type'),
                confidence=data.get('confidence'),
                price=data.get('price'),
                reasoning=data.get('reasoning'),
                ai_analysis=data.get('ai_analysis'),
                executed=data.get('executed', False)
            )
            
            self.db.add(signal)
            self.db.commit()
            self.db.refresh(signal)
            return signal
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error saving trading signal: {e}")
            raise
    
    def get_recent_signals(self, limit: int = 10) -> List[TradingSignal]:
        """Get recent trading signals"""
        try:
            return self.db.query(TradingSignal)\
                .order_by(TradingSignal.timestamp.desc())\
                .limit(limit)\
                .all()
        except Exception as e:
            logger.error(f"Error getting recent signals: {e}")
            raise
    
    # Bot Config methods
    def get_config(self, key: str) -> Any:
        """Get bot configuration value"""
        try:
            config = self.db.query(BotConfig)\
                .filter(BotConfig.key == key)\
                .first()
            
            if config:
                return json.loads(config.value)
            return None
        except Exception as e:
            logger.error(f"Error getting config: {e}")
            raise
    
    def update_config(self, key: str, value: Any) -> BotConfig:
        """Update bot configuration"""
        try:
            config = self.db.query(BotConfig)\
                .filter(BotConfig.key == key)\
                .first()
            
            if not config:
                config = BotConfig(
                    key=key,
                    value=json.dumps(value),
                    description=f"Added at {datetime.utcnow()}"
                )
                self.db.add(config)
            else:
                config.value = json.dumps(value)
                config.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(config)
            return config
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating config: {e}")
            raise
    
    # System Log methods
    def log_message(self, level: str, message: str, data: Any = None) -> SystemLog:
        """Log system message to database"""
        try:
            log = SystemLog(
                level=level.upper(),
                message=message,
                data=data
            )
            
            self.db.add(log)
            self.db.commit()
            self.db.refresh(log)
            return log
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error logging message: {e}")
            # Don't raise here to avoid recursive errors
            return None
