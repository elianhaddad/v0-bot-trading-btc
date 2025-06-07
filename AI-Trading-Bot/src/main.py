import argparse
from src.data_collector import get_historical_data
from src.data_preprocessor import preprocess_data

def main():
    parser = argparse.ArgumentParser(description="AI Trading Bot")
    parser.add_argument("--mode", choices=["backtest", "live", "ui"], required=True)
    args = parser.parse_args()

    if args.mode == "backtest":
        from src.backtesting import run_backtest_and_get_base64  # o run_backtest según tu implementación
        print("Iniciando Backtesting...")
        data = get_historical_data("AAPL", "2020-01-01", "2023-01-01")
        data = preprocess_data(data)
        image_data = run_backtest_and_get_base64(data)
        print("Backtest ejecutado. Imagen (base64):")
        print(image_data)
    elif args.mode == "ui":
        from src.ui import start_ui
        start_ui()
    elif args.mode == "live":
        print("Modo Live no implementado aún.")

if __name__ == "__main__":
    main()