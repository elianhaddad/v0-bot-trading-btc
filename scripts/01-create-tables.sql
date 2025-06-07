-- Tabla para almacenar datos de precios históricos
CREATE TABLE IF NOT EXISTS price_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(10) NOT NULL DEFAULT 'BTC/USDT',
    open DECIMAL(15,8) NOT NULL,
    high DECIMAL(15,8) NOT NULL,
    low DECIMAL(15,8) NOT NULL,
    close DECIMAL(15,8) NOT NULL,
    volume DECIMAL(20,8) NOT NULL,
    timeframe VARCHAR(5) NOT NULL DEFAULT '1m',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(timestamp, symbol, timeframe)
);

-- Tabla para indicadores técnicos
CREATE TABLE IF NOT EXISTS technical_indicators (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(10) NOT NULL DEFAULT 'BTC/USDT',
    rsi DECIMAL(8,4),
    macd DECIMAL(15,8),
    macd_signal DECIMAL(15,8),
    macd_histogram DECIMAL(15,8),
    bb_upper DECIMAL(15,8),
    bb_middle DECIMAL(15,8),
    bb_lower DECIMAL(15,8),
    ema_20 DECIMAL(15,8),
    ema_50 DECIMAL(15,8),
    sma_200 DECIMAL(15,8),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(timestamp, symbol)
);

-- Tabla para señales de trading
CREATE TABLE IF NOT EXISTS trading_signals (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(10) NOT NULL DEFAULT 'BTC/USDT',
    signal_type VARCHAR(10) NOT NULL CHECK (signal_type IN ('BUY', 'SELL', 'HOLD')),
    confidence DECIMAL(5,4) NOT NULL CHECK (confidence >= 0 AND confidence <= 1),
    price DECIMAL(15,8) NOT NULL,
    reasoning TEXT,
    ai_analysis JSONB,
    executed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla para configuración del bot
CREATE TABLE IF NOT EXISTS bot_config (
    id SERIAL PRIMARY KEY,
    key VARCHAR(50) UNIQUE NOT NULL,
    value JSONB NOT NULL,
    description TEXT,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Tabla para logs del sistema
CREATE TABLE IF NOT EXISTS system_logs (
    id SERIAL PRIMARY KEY,
    level VARCHAR(10) NOT NULL CHECK (level IN ('INFO', 'WARN', 'ERROR', 'DEBUG')),
    message TEXT NOT NULL,
    data JSONB,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para optimizar consultas
CREATE INDEX IF NOT EXISTS idx_price_data_timestamp ON price_data(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_price_data_symbol_timeframe ON price_data(symbol, timeframe);
CREATE INDEX IF NOT EXISTS idx_technical_indicators_timestamp ON technical_indicators(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_trading_signals_timestamp ON trading_signals(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_system_logs_timestamp ON system_logs(timestamp DESC);
