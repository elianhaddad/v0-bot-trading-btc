import { createServerClient } from "./supabase"
import { MarketDataService } from "./market-data"
import { TechnicalAnalysis } from "./technical-analysis"
import { AITradingService } from "./ai-trading"

export class TradingBot {
  private supabase = createServerClient()
  private marketData = MarketDataService.getInstance()
  private isRunning = false

  async start() {
    if (this.isRunning) return

    this.isRunning = true
    console.log("🤖 Bot de trading iniciado")

    // Ejecutar análisis cada minuto
    setInterval(() => {
      this.runAnalysis()
    }, 60000)

    // Ejecutar análisis inicial
    await this.runAnalysis()
  }

  async stop() {
    this.isRunning = false
    console.log("🛑 Bot de trading detenido")
  }

  private async runAnalysis() {
    try {
      // Verificar si el trading está habilitado
      const { data: config } = await this.supabase
        .from("bot_config")
        .select("value")
        .eq("key", "trading_enabled")
        .single()

      if (!config?.value || config.value === false) {
        return
      }

      // Obtener datos de mercado
      const currentPrice = await this.marketData.getCurrentPrice()
      const historicalData = await this.marketData.getHistoricalData()

      // Verificar si los datos están desactualizados
      if (this.marketData.isDataStale()) {
        await this.logMessage("WARN", "Datos de mercado desactualizados, actualizando...")
        this.marketData.updateLastUpdate()
      }

      // Guardar datos de precios
      await this.savePriceData(historicalData[historicalData.length - 1])

      // Calcular indicadores técnicos
      const prices = historicalData.map((d) => d.close)
      const indicators = TechnicalAnalysis.analyzeAll(prices)

      // Guardar indicadores
      await this.saveTechnicalIndicators(indicators)

      // Análisis con IA
      const aiAnalysis = await AITradingService.analyzeMarket({
        currentPrice: currentPrice.price,
        technicalIndicators: indicators,
        recentPrices: prices,
        volume: currentPrice.volume24h,
        marketTrend: this.determineTrend(prices),
      })

      // Guardar señal de trading
      if (aiAnalysis.confidence > 0.7) {
        await this.saveTradeSignal(aiAnalysis, currentPrice.price)
        await this.logMessage("INFO", `Señal generada: ${aiAnalysis.signal} con confianza ${aiAnalysis.confidence}`)
      }
    } catch (error) {
      await this.logMessage("ERROR", "Error en análisis del bot", { error: error.message })
    }
  }

  private async savePriceData(candle: any) {
    await this.supabase.from("price_data").upsert({
      timestamp: new Date(candle.timestamp),
      open: candle.open,
      high: candle.high,
      low: candle.low,
      close: candle.close,
      volume: candle.volume,
    })
  }

  private async saveTechnicalIndicators(indicators: any) {
    await this.supabase.from("technical_indicators").upsert({
      timestamp: new Date(),
      rsi: indicators.rsi,
      macd: indicators.macd.macd,
      macd_signal: indicators.macd.signal,
      macd_histogram: indicators.macd.histogram,
      bb_upper: indicators.bollingerBands.upper,
      bb_middle: indicators.bollingerBands.middle,
      bb_lower: indicators.bollingerBands.lower,
      ema_20: indicators.ema20,
      ema_50: indicators.ema50,
      sma_200: indicators.sma200,
    })
  }

  private async saveTradeSignal(signal: any, price: number) {
    await this.supabase.from("trading_signals").insert({
      timestamp: new Date(),
      signal_type: signal.signal,
      confidence: signal.confidence,
      price: price,
      reasoning: signal.reasoning,
      ai_analysis: signal,
    })
  }

  private async logMessage(level: string, message: string, data?: any) {
    await this.supabase.from("system_logs").insert({
      level,
      message,
      data,
    })

    console.log(`[${level}] ${message}`, data || "")
  }

  private determineTrend(prices: number[]): string {
    if (prices.length < 10) return "NEUTRAL"

    const recent = prices.slice(-10)
    const older = prices.slice(-20, -10)

    const recentAvg = recent.reduce((a, b) => a + b) / recent.length
    const olderAvg = older.reduce((a, b) => a + b) / older.length

    if (recentAvg > olderAvg * 1.01) return "UPTREND"
    if (recentAvg < olderAvg * 0.99) return "DOWNTREND"
    return "SIDEWAYS"
  }
}
