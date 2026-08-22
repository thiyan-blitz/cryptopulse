import {useState} from 'react'
import {useNavigate} from 'react-router-dom'
import Login from './Login'

function Signup(){
    const [username,setUsername]=useState('')
    const [password,setPassword]=useState('')
    const [email,setEmail]=useState('')
    const navigate=useNavigate()
    const [error,setError]=useState('')
    
    const handleSubmit=async (e)=>{
        e.preventDefault()
        setError('')

        try{
            const res=await fetch('http://localhost:8000/routes/auth/signup',{
                method:'POST',
                headers:{'Content-Type':'application/json'},
                body:JSON.stringify({username,password,email})
            })

        if (!res.ok){
            const  errData=await res.json()
            throw new Error(errData.detail || 'Signup failed')
        }
        navigate('/login')
        }
        catch(err){
            setError(err.message)
        }
    }

    return (
        <div className="p-8 max-w-md mx-auto">
            <h2 className="text-2xl font-bold mb-4">Signup</h2>
            <form onSubmit={handleSubmit} className="flex flex-col gap-3">

                <input
                    type="text"
                    placeholder="Username"
                    value={username}
                    onChange={(e)=>setUsername(e.target.value)}
                    className="border p-2 rounded"
                />
                <input
                    type="email"
                    placeholder="Email"
                    value={email}
                    onChange={(e)=>setEmail(e.target.value)}
                    className="border p-2 rounded"
                />
                <input
                    type="password"
                    placeholder="Password"
                    value={password}
                    onChange={(e)=>setPassword(e.target.value)}
                    className="border p-2 rounded"
                />  
                {error && <p className="text-red-600">{error}</p>}
                <button
                    className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    type="submit">
                    Signup
                </button>
            </form>
        </div>
        
    )
}

export default Signup