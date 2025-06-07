import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Get database URL from environment or use default
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost/trading_bot')

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create base class for models
Base = declarative_base()

# Logger
logger = logging.getLogger(__name__)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from src.database.models import Base
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise

def seed_initial_config(db=None):
    """Seed initial configuration"""
    from src.database.models import BotConfig
    import json
    
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Check if config already exists
        existing_config = db.query(BotConfig).first()
        if existing_config:
            logger.info("Initial configuration already exists")
            return
        
        # Initial configuration
        configs = [
            {
                "key": "trading_enabled",
                "value": json.dumps(False),
                "description": "Enable/disable automated trading"
            },
            {
                "key": "max_position_size",
                "value": json.dumps(0.01),
                "description": "Maximum position size in BTC"
            },
            {
                "key": "stop_loss_percentage",
                "value": json.dumps(0.02),
                "description": "Stop loss percentage (2%)"
            },
            {
                "key": "take_profit_percentage",
                "value": json.dumps(0.04),
                "description": "Take profit percentage (4%)"
            },
            {
                "key": "rsi_oversold",
                "value": json.dumps(30),
                "description": "RSI oversold level"
            },
            {
                "key": "rsi_overbought",
                "value": json.dumps(70),
                "description": "RSI overbought level"
            },
            {
                "key": "data_refresh_interval",
                "value": json.dumps(60),
                "description": "Data refresh interval in seconds"
            },
            {
                "key": "ai_confidence_threshold",
                "value": json.dumps(0.7),
                "description": "Minimum confidence threshold for AI signals"
            }
        ]
        
        for config in configs:
            db.add(BotConfig(**config))
        
        db.commit()
        logger.info("Initial configuration seeded successfully")
    except Exception as e:
        db.rollback()
        logger.error(f"Error seeding initial configuration: {e}")
        raise
    finally:
        if close_db:
            db.close()
