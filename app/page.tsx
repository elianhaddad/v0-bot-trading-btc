"use client"

import { useEffect, useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Switch } from "@/components/ui/switch"
import { supabase } from "@/lib/supabase"
import { MarketDataService } from "@/lib/market-data"
import { TrendingUp, TrendingDown, Activity, AlertTriangle } from "lucide-react"

interface MarketData {
  price: number
  change24h: number
  volume24h: number
  timestamp: number
}

interface TradingSignal {
  id: number
  signal_type: string
  confidence: number
  price: number
  reasoning: string
  timestamp: string
}

export default function Dashboard() {
  const [marketData, setMarketData] = useState<MarketData | null>(null)
  const [signals, setSignals] = useState<TradingSignal[]>([])
  const [botEnabled, setBotEnabled] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadDashboardData()

    // Actualizar datos cada 30 segundos
    const interval = setInterval(loadDashboardData, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadDashboardData = async () => {
    try {
      // Cargar datos de mercado
      const marketService = MarketDataService.getInstance()
      const currentPrice = await marketService.getCurrentPrice()
      setMarketData(currentPrice)

      // Cargar señales recientes
      const { data: signalsData } = await supabase
        .from("trading_signals")
        .select("*")
        .order("timestamp", { ascending: false })
        .limit(5)

      if (signalsData) {
        setSignals(signalsData)
      }

      // Cargar configuración del bot
      const { data: config } = await supabase.from("bot_config").select("value").eq("key", "trading_enabled").single()

      if (config) {
        setBotEnabled(config.value === true)
      }
    } catch (error) {
      console.error("Error loading dashboard data:", error)
    } finally {
      setLoading(false)
    }
  }

  const toggleBot = async () => {
    try {
      const newValue = !botEnabled

      await supabase.from("bot_config").update({ value: newValue }).eq("key", "trading_enabled")

      setBotEnabled(newValue)
    } catch (error) {
      console.error("Error toggling bot:", error)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-orange-500"></div>
      </div>
    )
  }

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Bot Trading BTC</h1>
          <p className="text-muted-foreground">Trading intradiario con IA</p>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-sm">Bot {botEnabled ? "Activo" : "Inactivo"}</span>
          <Switch checked={botEnabled} onCheckedChange={toggleBot} />
        </div>
      </div>

      {/* Datos de Mercado */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Precio BTC/USDT</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${marketData?.price.toLocaleString()}</div>
            <div
              className={`flex items-center text-xs ${
                marketData && marketData.change24h >= 0 ? "text-green-600" : "text-red-600"
              }`}
            >
              {marketData && marketData.change24h >= 0 ? (
                <TrendingUp className="h-3 w-3 mr-1" />
              ) : (
                <TrendingDown className="h-3 w-3 mr-1" />
              )}
              {marketData?.change24h.toFixed(2)}% (24h)
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Volumen 24h</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{marketData?.volume24h.toLocaleString()} BTC</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Estado del Sistema</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              <Badge variant={botEnabled ? "default" : "secondary"}>{botEnabled ? "Operativo" : "Pausado"}</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Señales Recientes */}
      <Card>
        <CardHeader>
          <CardTitle>Señales de Trading Recientes</CardTitle>
          <CardDescription>Últimas señales generadas por el sistema de IA</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {signals.map((signal) => (
              <div key={signal.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <Badge
                    variant={
                      signal.signal_type === "BUY"
                        ? "default"
                        : signal.signal_type === "SELL"
                          ? "destructive"
                          : "secondary"
                    }
                  >
                    {signal.signal_type}
                  </Badge>
                  <div>
                    <p className="font-medium">${signal.price.toLocaleString()}</p>
                    <p className="text-sm text-muted-foreground">Confianza: {(signal.confidence * 100).toFixed(1)}%</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">{new Date(signal.timestamp).toLocaleString()}</p>
                  <p className="text-xs text-muted-foreground max-w-xs truncate">{signal.reasoning}</p>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
