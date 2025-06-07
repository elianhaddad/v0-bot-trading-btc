interface TechnicalIndicators {
  rsi: number
  macd: {
    macd: number
    signal: number
    histogram: number
  }
  bollingerBands: {
    upper: number
    middle: number
    lower: number
  }
  ema20: number
  ema50: number
  sma200: number
}

export class TechnicalAnalysis {
  static calculateRSI(prices: number[], period = 14): number {
    if (prices.length < period + 1) return 50

    let gains = 0
    let losses = 0

    // Calcular ganancias y pérdidas iniciales
    for (let i = 1; i <= period; i++) {
      const change = prices[i] - prices[i - 1]
      if (change > 0) {
        gains += change
      } else {
        losses -= change
      }
    }

    let avgGain = gains / period
    let avgLoss = losses / period

    // Calcular RSI para el resto de los datos
    for (let i = period + 1; i < prices.length; i++) {
      const change = prices[i] - prices[i - 1]
      const gain = change > 0 ? change : 0
      const loss = change < 0 ? -change : 0

      avgGain = (avgGain * (period - 1) + gain) / period
      avgLoss = (avgLoss * (period - 1) + loss) / period
    }

    if (avgLoss === 0) return 100
    const rs = avgGain / avgLoss
    return 100 - 100 / (1 + rs)
  }

  static calculateEMA(prices: number[], period: number): number {
    if (prices.length === 0) return 0
    if (prices.length === 1) return prices[0]

    const multiplier = 2 / (period + 1)
    let ema = prices[0]

    for (let i = 1; i < prices.length; i++) {
      ema = prices[i] * multiplier + ema * (1 - multiplier)
    }

    return ema
  }

  static calculateSMA(prices: number[], period: number): number {
    if (prices.length < period) return 0

    const sum = prices.slice(-period).reduce((a, b) => a + b, 0)
    return sum / period
  }

  static calculateBollingerBands(prices: number[], period = 20, stdDev = 2) {
    const sma = this.calculateSMA(prices, period)
    const recentPrices = prices.slice(-period)

    const variance =
      recentPrices.reduce((sum, price) => {
        return sum + Math.pow(price - sma, 2)
      }, 0) / period

    const standardDeviation = Math.sqrt(variance)

    return {
      upper: sma + standardDeviation * stdDev,
      middle: sma,
      lower: sma - standardDeviation * stdDev,
    }
  }

  static analyzeAll(prices: number[]): TechnicalIndicators {
    const rsi = this.calculateRSI(prices)
    const ema20 = this.calculateEMA(prices, 20)
    const ema50 = this.calculateEMA(prices, 50)
    const sma200 = this.calculateSMA(prices, 200)
    const bollingerBands = this.calculateBollingerBands(prices)

    // MACD simplificado
    const ema12 = this.calculateEMA(prices, 12)
    const ema26 = this.calculateEMA(prices, 26)
    const macdLine = ema12 - ema26
    const signalLine = this.calculateEMA([macdLine], 9)
    const histogram = macdLine - signalLine

    return {
      rsi,
      macd: {
        macd: macdLine,
        signal: signalLine,
        histogram,
      },
      bollingerBands,
      ema20,
      ema50,
      sma200,
    }
  }
}
