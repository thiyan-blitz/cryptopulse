import { useState, useEffect } from 'react'
import { apiFetch } from '../utils/api'

function Dashboard() {
  const [portfolio, setPortfolio] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    apiFetch('/trade/portfolio')
      .then((data) => setPortfolio(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  if (loading) {
    return <div className="p-8 text-slate-300 animate-pulse">Loading portfolio...</div>
  }

  if (error) {
    return <div className="p-8 text-red-500 font-semibold">Error: {error}</div>
  }

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100">
      <h1 className="text-3xl font-bold mb-6 text-white tracking-tight">Dashboard</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-slate-800/80 backdrop-blur border border-slate-700/80 rounded-xl p-6 shadow-lg">
          <p className="text-slate-400 text-sm font-medium">Cash Balance</p>
          <p className="text-2xl font-bold text-white mt-2">
            ${Number(portfolio?.balance_usd || 0).toFixed(2)}
          </p>
        </div>

        <div className="bg-slate-800/80 backdrop-blur border border-slate-700/80 rounded-xl p-6 shadow-lg">
          <p className="text-slate-400 text-sm font-medium">Holdings Value</p>
          <p className="text-2xl font-bold text-white mt-2">
            ${Number(portfolio?.total_holdings_value || 0).toFixed(2)}
          </p>
        </div>

        <div className="bg-slate-800/80 backdrop-blur border border-slate-700/80 rounded-xl p-6 shadow-lg">
          <p className="text-slate-400 text-sm font-medium">Total Portfolio</p>
          <p className="text-2xl font-bold text-white mt-2">
            ${Number(portfolio?.total_portfolio_value || 0).toFixed(2)}
          </p>
        </div>
      </div>

      {/* Holdings Section */}
      <h2 className="text-2xl font-semibold mb-4 text-white">Holdings</h2>

      {!portfolio?.holdings || portfolio.holdings.length === 0 ? (
        <p className="text-slate-400">No holdings yet—head to Markets to start trading.</p>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {portfolio.holdings.map((h) => {
            const pnl = Number(h.pnl || 0)
            const pnlPct = Number(h.pnl_percent || 0)
            const isProfitable = pnl >= 0

            return (
              <div
                key={h.symbol}
                className="bg-slate-800/80 backdrop-blur border border-slate-700/80 rounded-xl p-6 shadow-md hover:border-slate-600 transition"
              >
                <p className="font-bold text-lg text-white mb-3">{h.symbol}</p>
                
                <div className="space-y-1.5 text-sm text-slate-300">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Qty:</span>
                    <span className="font-medium text-white">{h.quantity}</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-slate-400">Avg buy:</span>
                    <span>${Number(h.avg_buy_price || 0).toFixed(2)}</span>
                  </div>

                  <div className="flex justify-between">
                    <span className="text-slate-400">Current:</span>
                    <span>${Number(h.current_price || 0).toFixed(2)}</span>
                  </div>

                  <div className="flex justify-between pt-2 border-t border-slate-700/60 font-medium">
                    <span className="text-slate-400">P&L:</span>
                    <span className={isProfitable ? 'text-green-400' : 'text-red-400'}>
                      ${pnl.toFixed(2)} ({pnlPct.toFixed(2)}%)
                    </span>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

export default Dashboard