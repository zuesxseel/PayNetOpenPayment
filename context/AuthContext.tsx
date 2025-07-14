"use client"

import { createContext, useState, useContext } from "react"

const AuthContext = createContext({
  isAuthenticated: false,
  userType: "user", // "user" or "merchant"
  login: (type: string) => {},
  logout: () => {},
})

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [userType, setUserType] = useState("user")

  const login = (type = "user") => {
    setUserType(type)
    setIsAuthenticated(true)
  }

  const logout = () => {
    setIsAuthenticated(false)
    setUserType("user")
  }

  return <AuthContext.Provider value={{ isAuthenticated, userType, login, logout }}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  return useContext(AuthContext)
}
