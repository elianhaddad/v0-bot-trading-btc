from sqlalchemy import create_engine, Column, Integer, Float, String, DateTime, Boolean, JSON, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class PriceData(Base):
    __tablename__ = 'price_data'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, default='BTC/USDT')
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    timeframe = Column(String(5), default='1m')
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_symbol_timeframe_timestamp', 'symbol', 'timeframe', 'timestamp'),
    )

class TechnicalIndicator(Base):
    __tablename__ = 'technical_indicators'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, default='BTC/USDT')
    rsi = Column(Float)
    macd = Column(Float)
    macd_signal = Column(Float)
    macd_histogram = Column(Float)
    bb_upper = Column(Float)
    bb_middle = Column(Float)
    bb_lower = Column(Float)
    ema_20 = Column(Float)
    ema_50 = Column(Float)
    sma_200 = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

class TradingSignal(Base):
    __tablename__ = 'trading_signals'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, nullable=False, index=True)
    symbol = Column(String(20), nullable=False, default='BTC/USDT')
    signal_type = Column(String(10), nullable=False)  # BUY, SELL, HOLD
    confidence = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    reasoning = Column(String(500))
    ai_analysis = Column(JSON)
    executed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class BotConfig(Base):
    __tablename__ = 'bot_config'
    
    id = Column(Integer, primary_key=True)
    key = Column(String(50), unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(String(200))
    updated_at = Column(DateTime, default=datetime.utcnow)

class SystemLog(Base):
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True)
    level = Column(String(10), nullable=False)  # INFO, WARN, ERROR, DEBUG
    message = Column(String(500), nullable=False)
    data = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
