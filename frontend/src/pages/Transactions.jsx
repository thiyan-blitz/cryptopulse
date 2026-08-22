import { useState, useEffect } from 'react'
import { apiFetch } from '../utils/api'

function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [txType, setTxType] = useState('')
  const [timeRange, setTimeRange] = useState('')
  const [sortBy, setSortBy] = useState('created_at')
  const [sortOrder, setSortOrder] = useState('desc')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const fetchTransactions = () => {
    setLoading(true)
    const params = new URLSearchParams()
    if (txType) params.append('tx_type', txType)
    if (timeRange) params.append('time_range', timeRange)
    params.append('sort_by', sortBy)
    params.append('sort_order', sortOrder)

    apiFetch(`/trade/transactions?${params.toString()}`)
      .then((data) => setTransactions(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }

  useEffect(() => {
    fetchTransactions()
  }, [txType, timeRange, sortBy, sortOrder])

  return (
    <div className="p-8 max-w-7xl mx-auto text-slate-100">
      <h1 className="text-3xl font-bold mb-6 text-white tracking-tight">Transaction History</h1>

      {/* Filter Controls */}
      <div className="flex flex-wrap gap-3 mb-6">
        <select
          value={txType}
          onChange={(e) => setTxType(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 outline-none focus:border-blue-500 text-sm font-medium"
        >
          <option value="">All Types</option>
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
        </select>

        <select
          value={timeRange}
          onChange={(e) => setTimeRange(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 outline-none focus:border-blue-500 text-sm font-medium"
        >
          <option value="">All Time</option>
          <option value="last_hour">Last Hour</option>
          <option value="last_day">Last Day</option>
          <option value="last_week">Last Week</option>
          <option value="last_month">Last Month</option>
        </select>

        <select
          value={sortBy}
          onChange={(e) => setSortBy(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 outline-none focus:border-blue-500 text-sm font-medium"
        >
          <option value="created_at">Date</option>
          <option value="price_at_trade">Price</option>
          <option value="quantity">Quantity</option>
          <option value="total_value">Total Value</option>
        </select>

        <select
          value={sortOrder}
          onChange={(e) => setSortOrder(e.target.value)}
          className="bg-slate-800 border border-slate-700 text-white rounded-lg p-2.5 outline-none focus:border-blue-500 text-sm font-medium"
        >
          <option value="desc">Descending</option>
          <option value="asc">Ascending</option>
        </select>
      </div>

      {loading && (
        <div className="p-8 text-slate-400 animate-pulse">Loading transactions...</div>
      )}

      {error && (
        <div className="p-4 mb-4 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-sm font-medium">
          {error}
        </div>
      )}

      {!loading && !error && (
        <div className="bg-slate-800/80 backdrop-blur border border-slate-700/80 rounded-xl overflow-hidden shadow-xl">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-900/60 border-b border-slate-700/80 text-slate-400 text-xs uppercase tracking-wider font-semibold">
                <th className="p-4">Asset</th>
                <th className="p-4">Type</th>
                <th className="p-4">Quantity</th>
                <th className="p-4">Price</th>
                <th className="p-4">Total Value</th>
                <th className="p-4">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-700/50 text-sm">
              {transactions.length === 0 ? (
                <tr>
                  <td colSpan="6" className="p-6 text-center text-slate-400">
                    No transactions found.
                  </td>
                </tr>
              ) : (
                transactions.map((tx) => (
                  <tr key={tx.id} className="hover:bg-slate-700/30 transition">
                    <td className="p-4 font-bold text-white">
                      {tx.symbol || 'N/A'}
                    </td>
                    <td className={`p-4 font-bold ${tx.tx_type === 'buy' ? 'text-green-400' : 'text-red-400'}`}>
                      {tx.tx_type.toUpperCase()}
                    </td>
                    <td className="p-4 text-slate-200">{tx.quantity}</td>
                    <td className="p-4 text-slate-200">${Number(tx.price_at_trade).toFixed(2)}</td>
                    <td className="p-4 text-slate-200">${Number(tx.total_value).toFixed(2)}</td>
                    <td className="p-4 text-slate-400">{new Date(tx.created_at).toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default Transactions