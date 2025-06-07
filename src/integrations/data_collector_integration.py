import logging
import sys
import os
import time
from typing import List, Dict, Any
import importlib.util

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.services.data_service import DataService
from src.database.connection import get_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DataCollectorIntegration:
    def __init__(self):
        """Initialize data collector integration"""
        self.db = next(get_db())
        self.data_service = DataService(self.db)
        
        # Try to import your existing data collector
        try:
            # Dynamically import your data collector module
            spec = importlib.util.spec_from_file_location(
                "data_collector", 
                os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                            "src/data-collector/collector.py")
            )
            self.data_collector_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(self.data_collector_module)
            
            # Get the data collector class
            self.data_collector = self.data_collector_module.DataCollector()
            logger.info("Successfully imported existing data collector")
        except Exception as e:
            logger.error(f"Error importing data collector: {e}")
            self.data_collector = None
    
    def __del__(self):
        """Close database connection"""
        if hasattr(self, 'db'):
            self.db.close()
    
    def process_candles(self, candles: List[Dict[str, Any]]) -> bool:
        """Process candles and store in database"""
        try:
            return self.data_service.store_candle_batch(candles)
        except Exception as e:
            logger.error(f"Error processing candles: {e}")
            return False
    
    def run(self, interval: int = 60):
        """Run data collector integration"""
        logger.info("Starting data collector integration")
        
        while True:
            try:
                # Check if data is stale
                if self.data_service.is_data_stale(max_age_seconds=interval):
                    logger.info("Data is stale, collecting new data")
                    
                    # Use your existing data collector
                    if self.data_collector:
                        # Assuming your data collector has a get_candles method
                        candles = self.data_collector.get_candles()
                        if candles:
                            self.process_candles(candles)
                            logger.info(f"Processed {len(candles)} candles")
                    else:
                        logger.warning("Data collector not available")
                
                # Sleep for interval
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Error in data collector integration: {e}")
                time.sleep(interval)

if __name__ == "__main__":
    integration = DataCollectorIntegration()
    integration.run()
