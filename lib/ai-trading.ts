import { generateObject } from "ai"
import { openai } from "@ai-sdk/openai"
import { z } from "zod"

const TradingSignalSchema = z.object({
  signal: z.enum(["BUY", "SELL", "HOLD"]),
  confidence: z.number().min(0).max(1),
  reasoning: z.string(),
  targetPrice: z.number().optional(),
  stopLoss: z.number().optional(),
  takeProfit: z.number().optional(),
})

interface MarketContext {
  currentPrice: number
  technicalIndicators: any
  recentPrices: number[]
  volume: number
  marketTrend: string
}

export class AITradingService {
  static async analyzeMarket(context: MarketContext) {
    try {
      const { object } = await generateObject({
        model: openai("gpt-4o-mini"),
        schema: TradingSignalSchema,
        prompt: `
          Analiza los siguientes datos de mercado para BTC/USDT y proporciona una señal de trading:

          Precio actual: $${context.currentPrice}
          
          Indicadores técnicos:
          - RSI: ${context.technicalIndicators.rsi}
          - MACD: ${context.technicalIndicators.macd.macd}
          - Señal MACD: ${context.technicalIndicators.macd.signal}
          - EMA 20: ${context.technicalIndicators.ema20}
          - EMA 50: ${context.technicalIndicators.ema50}
          - Bollinger Superior: ${context.technicalIndicators.bollingerBands.upper}
          - Bollinger Inferior: ${context.technicalIndicators.bollingerBands.lower}
          
          Precios recientes: ${context.recentPrices.slice(-10).join(", ")}
          Volumen: ${context.volume}
          Tendencia del mercado: ${context.marketTrend}

          Considera:
          1. Trading intradiario (posiciones de corta duración)
          2. Gestión de riesgo conservadora
          3. Señales técnicas claras
          4. Volatilidad del mercado
          5. Volumen de trading

          Proporciona una señal clara con alta confianza solo si hay una oportunidad evidente.
        `,
      })

      return object
    } catch (error) {
      console.error("Error en análisis de IA:", error)
      return {
        signal: "HOLD" as const,
        confidence: 0,
        reasoning: "Error en el análisis de IA",
      }
    }
  }

  static async getMarketSentiment(newsData?: string[]) {
    try {
      const { object } = await generateObject({
        model: openai("gpt-4o-mini"),
        schema: z.object({
          sentiment: z.enum(["BULLISH", "BEARISH", "NEUTRAL"]),
          score: z.number().min(-1).max(1),
          summary: z.string(),
        }),
        prompt: `
          Analiza el sentimiento del mercado de Bitcoin basándote en:
          ${newsData ? `Noticias recientes: ${newsData.join("\n")}` : "Análisis técnico general del mercado"}
          
          Proporciona:
          1. Sentimiento general (BULLISH/BEARISH/NEUTRAL)
          2. Puntuación de -1 (muy bajista) a 1 (muy alcista)
          3. Resumen del análisis
        `,
      })

      return object
    } catch (error) {
      console.error("Error en análisis de sentimiento:", error)
      return {
        sentiment: "NEUTRAL" as const,
        score: 0,
        summary: "No se pudo analizar el sentimiento",
      }
    }
  }
}
