import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

function Markets() {
  const [prices, setPrices] = useState({})
  const [connected, setConnected] = useState(false)

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/prices")
    ws.onopen = () => setConnected(true)
    ws.onclose = () => setConnected(false)
    ws.onmessage = (event) => {
      setPrices(JSON.parse(event.data))
    }
    return () => ws.close()
  }, [])

  const sortedCoins = Object.entries(prices).sort((a, b) => a[0].localeCompare(b[0]))

  return (
    <div className="p-8">
      <h1 className="text-2xl font-bold mb-2">Markets</h1>
      <p className="mb-4 text-sm text-gray-400">{connected ? "🟢 Live" : "🔴 Disconnected"}</p>

      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b text-left">
            <th className="p-2">Coin</th>
            <th className="p-2">Price</th>
            <th className="p-2">24h Change</th>
            <th className="p-2">24h High</th>
            <th className="p-2">24h Low</th>
            <th className="p-2"></th>
          </tr>
        </thead>
        <tbody>
          {sortedCoins.map(([symbol, data]) => (
            <tr key={symbol} className="border-b hover:bg-white/5">
              <td className="p-2 font-bold">{symbol}</td>
              <td className="p-2">${data.price}</td>
              <td className={`p-2 ${data.change_pct >= 0 ? "text-green-500" : "text-red-500"}`}>
                {data.change_pct}%
              </td>
              <td className="p-2">${data.high}</td>
              <td className="p-2">${data.low}</td>
              <td className="p-2">
                <Link to={`/trade/${symbol}`} className="text-blue-400 underline">
                  Trade
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default Markets