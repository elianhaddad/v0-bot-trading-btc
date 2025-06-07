import unittest
from src.execution import send_order_buy, send_order_sell

class TestExecution(unittest.TestCase):
    def test_send_order_buy(self):
        # Aquí se puede verificar la salida o comportamiento de la función
        send_order_buy("AAPL", 10)

    def test_send_order_sell(self):
        send_order_sell("AAPL", 10)

if __name__ == '__main__':
    unittest.main()