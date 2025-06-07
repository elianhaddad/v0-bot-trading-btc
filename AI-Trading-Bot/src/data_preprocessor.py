import pandas as pd

def preprocess_data(data):
    print("Procesando datos...")
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data.dropna(inplace=True)
    data.reset_index(drop=True, inplace=True)
    return data