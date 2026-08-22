import {useState,useEffect} from 'react'
import {Link} from 'react-router-dom'
function PriceTicker(){
  const [prices,setPrices]=useState({})
  const [connected,setConnected]=useState(false)

  useEffect(   ()=>{
    const ws=new WebSocket("ws://localhost:8000/ws/prices")
    ws.onopen=()=>setConnected(true)
    ws.onmessage=(event)=>{
      const data=JSON.parse(event.data)
      setPrices(data)
    }
    return ()=>ws.close()
  }  ,[])

  return (
    <div className="p-8">
      <p className="mb-4">{connected? "connected": "disconnected"}</p>

      <div className="grid grid-cols-2 gap-4">
        {Object.entries(prices).map(([symbol,data])=>(

          <Link key={symbol} to={`/trade/${symbol}`} className="p-4 border rounded hover:bg-gray-50 block">
            <p className="text-lg font-bold">{symbol}</p>
            <p className="text-gray-600">${data.price}</p>
            <p className={data.change_pct>=0 ? "text-green-500" : "text-red-600"}>
              {data.change_pct}%
            </p>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default PriceTicker
