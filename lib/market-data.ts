interface CandleData {
  timestamp: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

interface MarketData {
  symbol: string
  price: number
  change24h: number
  volume24h: number
  timestamp: number
}

export class MarketDataService {
  private static instance: MarketDataService
  private lastUpdate = 0
  private readonly UPDATE_INTERVAL = 60000 // 1 minuto

  static getInstance(): MarketDataService {
    if (!MarketDataService.instance) {
      MarketDataService.instance = new MarketDataService()
    }
    return MarketDataService.instance
  }

  async getCurrentPrice(symbol = "BTCUSDT"): Promise<MarketData> {
    try {
      const response = await fetch(`https://api.binance.com/api/v3/ticker/24hr?symbol=${symbol}`)

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      return {
        symbol: data.symbol,
        price: Number.parseFloat(data.lastPrice),
        change24h: Number.parseFloat(data.priceChangePercent),
        volume24h: Number.parseFloat(data.volume),
        timestamp: Date.now(),
      }
    } catch (error) {
      console.error("Error fetching current price:", error)
      throw error
    }
  }

  async getHistoricalData(symbol = "BTCUSDT", interval = "1m", limit = 100): Promise<CandleData[]> {
    try {
      const response = await fetch(
        `https://api.binance.com/api/v3/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`,
      )

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }

      const data = await response.json()

      return data.map((candle: any[]) => ({
        timestamp: candle[0],
        open: Number.parseFloat(candle[1]),
        high: Number.parseFloat(candle[2]),
        low: Number.parseFloat(candle[3]),
        close: Number.parseFloat(candle[4]),
        volume: Number.parseFloat(candle[5]),
      }))
    } catch (error) {
      console.error("Error fetching historical data:", error)
      throw error
    }
  }

  isDataStale(): boolean {
    return Date.now() - this.lastUpdate > this.UPDATE_INTERVAL
  }

  updateLastUpdate(): void {
    this.lastUpdate = Date.now()
  }
}
