import os
import sys
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.init_db import main as init_db_main

if __name__ == "__main__":
    print("Setting up database...")
    init_db_main()
    print("Database setup complete!")
