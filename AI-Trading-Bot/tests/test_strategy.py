import unittest
import pandas as pd
from src.strategy.trend_following import generate_signals

class TestStrategy(unittest.TestCase):
    def test_generate_signals(self):
        # Crear un DataFrame de ejemplo
        data = pd.DataFrame({
            "Close": [100, 105, 102, 107, 103],
            "SMA20": [102, 102, 102, 102, 102]
        })
        data = generate_signals(data)
        self.assertIn("Signal", data.columns)

if __name__ == '__main__':
    unittest.main()