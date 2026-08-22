import { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine
} from 'recharts'
import { apiFetch } from '../utils/api'

const COINS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "SOLUSDT", "XRPUSDT", "ADAUSDT", "DOGEUSDT", "DOTUSDT", "POLUSDT", "AVAXUSDT"]

function Analytics() {
  const { symbol = 'BTCUSDT' } = useParams()
  const navigate = useNavigate()
  const [candles, setCandles] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    setLoading(true)
    apiFetch(`/analytics/${symbol}?interval=1h`)
      .then((data) => {
        const formatted = (data?.candles || []).map((c) => ({
          ts: new Date(c.ts).toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit' }),
          close: Number(c.close || 0),
          sma_20: c.sma_20 ? Number(c.sma_20) : null,
          rsi_14: c.rsi_14 ? Number(c.rsi_14) : null,
        }))
        setCandles(formatted)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [symbol])

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100">
      
      {/* Top Header & Market Selector */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white tracking-tight">{symbol} Analytics</h1>
          <p className="text-sm text-slate-400 mt-1">Price movement & technical indicators</p>
        </div>

        <select
          value={symbol}
          onChange={(e) => navigate(`/analytics/${e.target.value}`)}
          className="bg-slate-800 border border-slate-700 text-white font-medium py-2 px-4 rounded-lg outline-none focus:border-blue-500 cursor-pointer w-fit"
        >
          {COINS.map((c) => (
            <option key={c} value={c}>{c}</option>
          ))}
        </select>
      </div>

      {loading && (
        <div className="p-12 text-center text-slate-400 bg-slate-800/40 rounded-2xl border border-slate-800 animate-pulse">
          Loading analytics & market data...
        </div>
      )}

      {error && (
        <div className="p-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium">
          {error}
        </div>
      )}

      {!loading && !error && (
        <div className="space-y-8">
          
          {/* Price + SMA(20) Card */}
          <div className="bg-slate-800/80 backdrop-blur border border-slate-700/80 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Price + SMA (20)</h2>
              <div className="flex items-center gap-4 text-xs font-semibold">
                <span className="flex items-center gap-1.5 text-blue-400">
                  <span className="w-3 h-0.5 bg-blue-500 inline-block"></span> Price
                </span>
                <span className="flex items-center gap-1.5 text-amber-400">
                  <span className="w-3 h-0.5 bg-amber-500 inline-block"></span> SMA 20
                </span>
              </div>
            </div>

            <div className="w-full h-[350px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={candles} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="ts" tick={{ fill: '#94a3b8', fontSize: 11 }} stroke="#475569" />
                  <YAxis domain={['auto', 'auto']} tick={{ fill: '#94a3b8', fontSize: 11 }} stroke="#475569" tickFormatter={(v) => `$${v}`} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                    formatter={(value) => [`$${Number(value).toFixed(2)}`]}
                  />
                  <Line type="monotone" dataKey="close" stroke="#3b82f6" strokeWidth={2} dot={false} name="Price" />
                  <Line type="monotone" dataKey="sma_20" stroke="#f59e0b" strokeWidth={2} dot={false} name="SMA 20" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* RSI (14) Card */}
          <div className="bg-slate-800/80 backdrop-blur border border-slate-700/80 rounded-2xl p-6 shadow-xl">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Relative Strength Index (RSI 14)</h2>
              <div className="flex items-center gap-4 text-xs font-semibold">
                <span className="text-red-400">Overbought (&gt;70)</span>
                <span className="text-green-400">Oversold (&lt;30)</span>
              </div>
            </div>

            <div className="w-full h-[220px]">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={candles} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                  <XAxis dataKey="ts" tick={{ fill: '#94a3b8', fontSize: 11 }} stroke="#475569" />
                  <YAxis domain={[0, 100]} tick={{ fill: '#94a3b8', fontSize: 11 }} stroke="#475569" />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', color: '#fff' }}
                    formatter={(value) => [Number(value).toFixed(2), 'RSI']}
                  />
                  <ReferenceLine y={70} stroke="#ef4444" strokeDasharray="4 4" />
                  <ReferenceLine y={30} stroke="#22c55e" strokeDasharray="4 4" />
                  <Line type="monotone" dataKey="rsi_14" stroke="#a855f7" strokeWidth={2} dot={false} name="RSI 14" />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

        </div>
      )}
    </div>
  )
}

export default Analytics