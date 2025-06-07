import unittest
from src.data_collector import get_historical_data

class TestDataCollector(unittest.TestCase):
    def test_get_historical_data(self):
        data = get_historical_data("AAPL", "2020-01-01", "2020-01-31")
        self.assertFalse(data.empty)

if __name__ == '__main__':
    unittest.main()