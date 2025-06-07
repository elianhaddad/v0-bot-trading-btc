import { type NextRequest, NextResponse } from "next/server"
import { TradingBot } from "@/lib/trading-bot"

let botInstance: TradingBot | null = null

export async function POST(request: NextRequest) {
  try {
    const { action } = await request.json()

    if (action === "start") {
      if (!botInstance) {
        botInstance = new TradingBot()
      }
      await botInstance.start()
      return NextResponse.json({ success: true, message: "Bot iniciado" })
    }

    if (action === "stop") {
      if (botInstance) {
        await botInstance.stop()
      }
      return NextResponse.json({ success: true, message: "Bot detenido" })
    }

    return NextResponse.json({ success: false, message: "Acción no válida" })
  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        message: "Error en el servidor",
        error: error.message,
      },
      { status: 500 },
    )
  }
}
