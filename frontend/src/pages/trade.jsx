import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { apiFetch } from '../utils/api'

const COINS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT", "POLUSDT", "AVAXUSDT"]

function Trade() {
  const { symbol = 'BTCUSDT' } = useParams()
  const navigate = useNavigate()
  const [livePrice, setLivePrice] = useState(null)
  const [quantity, setQuantity] = useState('')
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    const ws = new WebSocket("ws://localhost:8000/ws/prices")
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      if (data[symbol]) {
        setLivePrice(data[symbol])
      }
    }
    return () => ws.close()
  }, [symbol])

  const handleTrade = async (type) => {
    setError('')
    setMessage('')
    setLoading(true)

    try {
      const result = await apiFetch(`/trade/${type}`, {
        method: 'POST',
        body: JSON.stringify({ symbol, quantity: parseFloat(quantity) }),
      })
      setMessage(
        `${type === 'buy' ? 'Bought' : 'Sold'} ${result.quantity} ${result.symbol} at $${result.price_at_trade}. New balance: $${Number(result.new_balance).toFixed(2)}`
      )
      setQuantity('')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const currentPrice = Number(livePrice?.price || 0)
  const estimatedTotal = currentPrice * (parseFloat(quantity) || 0)

  return (
    <div className="p-8 max-w-xl mx-auto text-slate-100">
      <div className="bg-slate-800/80 backdrop-blur border border-slate-700/80 rounded-2xl p-6 shadow-xl">
        
        {/* Top Controls */}
        <div className="flex items-center justify-between mb-6 pb-4 border-b border-slate-700/60">
          <label className="text-sm font-semibold text-slate-400 uppercase tracking-wider">Select Market</label>
          <select
            value={symbol}
            onChange={(e) => navigate(`/trade/${e.target.value}`)}
            className="bg-slate-900 border border-slate-700 text-white font-medium py-2 px-4 rounded-lg outline-none focus:border-blue-500 cursor-pointer"
          >
            {COINS.map((c) => (
              <option key={c} value={c}>{c}</option>
            ))}
          </select>
        </div>

        {/* Live Market Price Section */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-white mb-1">{symbol}</h1>
          {livePrice ? (
            <div>
              <p className="text-4xl font-extrabold text-white tracking-tight">
                ${Number(livePrice.price).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 8 })}
              </p>
              <p className={`text-sm font-semibold mt-1 ${livePrice.change_pct >= 0 ? "text-green-400" : "text-red-400"}`}>
                {livePrice.change_pct >= 0 ? `+${livePrice.change_pct}%` : `${livePrice.change_pct}%`} (24h)
              </p>
            </div>
          ) : (
            <div className="animate-pulse space-y-2 py-2">
              <div className="h-8 bg-slate-700 rounded w-1/2"></div>
              <div className="h-4 bg-slate-700/60 rounded w-1/4"></div>
            </div>
          )}
        </div>

        {/* Order Form */}
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-400 mb-1.5">Order Quantity</label>
            <input
              type="number"
              step="any"
              placeholder="0.00"
              value={quantity}
              onChange={(e) => setQuantity(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded-lg p-3 text-white placeholder-slate-500 outline-none focus:border-blue-500 font-medium transition"
            />
          </div>

          {/* Dynamic Order Calculation */}
          {quantity > 0 && currentPrice > 0 && (
            <div className="flex justify-between items-center text-sm py-2 px-3 bg-slate-900/60 rounded-lg border border-slate-700/50">
              <span className="text-slate-400">Estimated Total:</span>
              <span className="font-bold text-white">${estimatedTotal.toFixed(2)}</span>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex gap-4 pt-2">
            <button
              onClick={() => handleTrade('buy')}
              disabled={loading || !quantity}
              className="flex-1 bg-green-600 hover:bg-green-500 active:bg-green-700 text-white font-bold py-3 px-4 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
            >
              {loading ? 'Processing...' : 'Buy'}
            </button>
            <button
              onClick={() => handleTrade('sell')}
              disabled={loading || !quantity}
              className="flex-1 bg-red-600 hover:bg-red-500 active:bg-red-700 text-white font-bold py-3 px-4 rounded-lg transition disabled:opacity-50 disabled:cursor-not-allowed shadow-md"
            >
              {loading ? 'Processing...' : 'Sell'}
            </button>
          </div>
        </div>

        {/* Feedback Messages */}
        {message && (
          <div className="mt-5 p-3 rounded-lg bg-green-500/10 border border-green-500/30 text-green-400 text-sm font-medium">
            {message}
          </div>
        )}
        {error && (
          <div className="mt-5 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium">
            {error}
          </div>
        )}

      </div>
    </div>
  )
}

export default Trade