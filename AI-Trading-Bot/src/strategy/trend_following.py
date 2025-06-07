def generate_signals(data):
    print("Generando señales para trend following...")
    # Ejemplo: si el precio es mayor que la SMA, señal de compra; de lo contrario, señal de venta.
    data['Signal'] = 0
    data.loc[data['Close'] > data['SMA20'], 'Signal'] = 1
    data.loc[data['Close'] < data['SMA20'], 'Signal'] = -1
    return data