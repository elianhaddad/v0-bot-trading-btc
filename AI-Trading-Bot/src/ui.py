import os
from flask import Flask, render_template, jsonify
import time
import random

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')
app = Flask(__name__, template_folder=TEMPLATE_DIR)


# Datos simulados para el ejemplo (en un escenario real, usarías datos reales)
# Por ejemplo, podrías actualizar esta variable en un proceso en segundo plano
latest_data = {
    "timestamp": time.time(),
    "cumulative": 1.0  # rendimiento inicial
}

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/backtest")
def backtest():
    # Aquí deberías incluir la lógica que genera el gráfico y lo pasa a la plantilla chart.html
    # Por ejemplo:
    from src.data_collector import get_historical_data
    from src.data_preprocessor import preprocess_data
    from src.backtesting import run_backtest_and_get_base64

    data = get_historical_data("AAPL", "2020-01-01", "2023-01-01")
    data = preprocess_data(data)
    chart_data = run_backtest_and_get_base64(data)
    return render_template("chart.html", chart_data=chart_data)


@app.route("/data")
def data():
    # Aquí podrías actualizar los datos con la lógica real de tu bot
    # Este ejemplo simula una actualización aleatoria para el rendimiento acumulado
    global latest_data
    latest_data["timestamp"] = time.time()
    latest_data["cumulative"] = latest_data["cumulative"] * (1 + (random.random() - 0.5) / 50)
    return jsonify(latest_data)



def start_ui():
    app.run(debug=True)

# Esto permite ejecutar la app directamente con "python src/ui.py"
if __name__ == "__main__":
    start_ui()