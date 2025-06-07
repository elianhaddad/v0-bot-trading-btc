-- Configuración inicial del bot
INSERT INTO bot_config (key, value, description) VALUES
('trading_enabled', 'false', 'Habilitar/deshabilitar trading automático'),
('max_position_size', '0.01', 'Tamaño máximo de posición en BTC'),
('stop_loss_percentage', '0.02', 'Porcentaje de stop loss (2%)'),
('take_profit_percentage', '0.04', 'Porcentaje de take profit (4%)'),
('rsi_oversold', '30', 'Nivel RSI de sobreventa'),
('rsi_overbought', '70', 'Nivel RSI de sobrecompra'),
('data_refresh_interval', '60', 'Intervalo de actualización de datos en segundos'),
('ai_confidence_threshold', '0.7', 'Umbral mínimo de confianza para ejecutar señales')
ON CONFLICT (key) DO NOTHING;
