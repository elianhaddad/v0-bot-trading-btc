# import matplotlib.pyplot as plt
# import numpy as np

# def run_backtest(data, strategy):
#     print(f"Ejecutando backtesting con la estrategia: {strategy}")
    
#     # Verificar que las columnas requeridas existan
#     if 'Close' not in data.columns or 'SMA20' not in data.columns:
#         raise ValueError("El DataFrame debe contener las columnas 'Close' y 'SMA20'")
    
#     # Convertir las columnas a arrays 1D
#     close = data['Close'].to_numpy().flatten()
#     sma = data['SMA20'].to_numpy().flatten()
    
#     print("Forma de close:", close.shape)
#     print("Forma de SMA20:", sma.shape)
    
#     # Comparar elemento a elemento
#     signal = (close > sma).astype(int)
    
#     # Asignar la señal a la columna 'Signal'
#     data = data.copy()  # Evitar problemas con vistas
#     data['Signal'] = signal
    
#     # Calcular retornos y la rentabilidad de la estrategia
#     data['Return'] = data['Close'].pct_change()
#     data['Strategy_Return'] = data['Return'] * data['Signal'].shift(1)
#     data['Cumulative_Strategy'] = (1 + data['Strategy_Return']).cumprod()
    
#     # Graficar resultados
#     plt.figure(figsize=(10, 5))
#     plt.plot(data.index, data['Cumulative_Strategy'], label="Estrategia")
#     plt.xlabel("Fecha")
#     plt.ylabel("Rendimiento Acumulado")
#     plt.title("Backtesting de la Estrategia")
#     plt.legend()
#     plt.show()


import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import io
import base64

def run_backtest_and_get_base64(data):
    # Convertir las columnas a arrays 1D
    close = data['Close'].to_numpy().flatten()
    sma   = data['SMA20'].to_numpy().flatten()
    
    # Depuración: imprime las formas para confirmar que sean 1D
    print("Shape of close:", close.shape)  # Debería ser (n,)
    print("Shape of SMA20:", sma.shape)      # Debería ser (n,)
    
    # Comparación elemento a elemento
    signal = (close > sma).astype(int)
    
    # Asignar la señal al DataFrame (aseguramos que el array tenga la misma longitud)
    data = data.copy()
    data['Signal'] = signal

    # Calcular retornos y rentabilidad de la estrategia
    data['Return'] = data['Close'].pct_change()
    data['Strategy_Return'] = data['Return'] * data['Signal'].shift(1)
    data['Cumulative_Strategy'] = (1 + data['Strategy_Return']).cumprod()

    # Crear el gráfico
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(data.index, data['Cumulative_Strategy'], label="Estrategia")
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Rendimiento Acumulado")
    ax.set_title("Backtesting de la Estrategia")
    ax.legend()

    # Convertir el gráfico a imagen PNG en base64
    png_image = io.BytesIO()
    fig.savefig(png_image, format='png')
    plt.close(fig)
    png_image.seek(0)
    base64_image = base64.b64encode(png_image.getvalue()).decode('ascii')
    return base64_image