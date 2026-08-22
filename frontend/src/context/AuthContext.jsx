import {createContext, useContext, useState} from "react";

const AuthContext=createContext(null)

export const AuthProvider=({children})=>{
    const [accessToken,setAccessToken]=useState(localStorage.getItem('access_token'));
    
    const login=(access,refresh)=>{
        localStorage.setItem('access_token',access)
        localStorage.setItem('refresh_token',refresh)
        setAccessToken(access)
    }

    const logout=()=>{
        localStorage.removeItem('access_token')
        localStorage.removeItem('refresh_token')
        setAccessToken(null)    
    }

    return (
        <AuthContext.Provider value={{accessToken,isLoggedIn:!!accessToken,login,logout}}>
            {children}
        </AuthContext.Provider>
    )
}

export function useAuth(){
    return useContext(AuthContext)
}

