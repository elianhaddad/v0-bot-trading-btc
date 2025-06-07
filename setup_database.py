import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.database.connection import init_db

def setup_database():
    """Setup the PostgreSQL database"""
    try:
        print("Setting up PostgreSQL database...")
        init_db()
        print("✅ Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up your .env file with database credentials")
        print("3. Run your data collector: python data_collector.py")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        print("\nMake sure PostgreSQL is running and credentials are correct in .env file")

if __name__ == "__main__":
    setup_database()
