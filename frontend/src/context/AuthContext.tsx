import {
  createContext,
  useContext,
  useEffect,
  useState,
  type ReactNode,
} from 'react'
import { authService } from '../services/authService'
import { getAccessToken } from '../utils/authToken'
import type { User, LoginRequest } from '../types/auth'
import type { ApiError } from '../types/api'

interface AuthContextValue {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (credentials: LoginRequest) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined)

interface AuthProviderProps {
  children: ReactNode
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(true)

  useEffect(() => {
    let isMounted = true

    async function initializeAuth() {
      const token = getAccessToken()

      if (!token) {
        if (isMounted) {
          setIsLoading(false)
        }
        return
      }

      try {
        const currentUser = await authService.getCurrentUser()
        if (isMounted) {
          setUser(currentUser)
        }
      } catch (error) {
        const apiError = error as ApiError

        // Only a confirmed 401 means the stored token is actually invalid
        // or expired. Any other error (network failure, 500, etc.) should
        // not be treated as "logged out" — we simply leave the token and
        // user state untouched and let a later request try again.
        if (apiError.status === 401) {
          authService.logout()
          if (isMounted) {
            setUser(null)
          }
        }
      } finally {
        if (isMounted) {
          setIsLoading(false)
        }
      }
    }

    initializeAuth()

    return () => {
      isMounted = false
    }
  }, [])

  async function login(credentials: LoginRequest): Promise<void> {
    // authService.login() already stores the access token internally.
    await authService.login(credentials)
    const currentUser = await authService.getCurrentUser()
    setUser(currentUser)
  }

  function logout(): void {
    authService.logout()
    setUser(null)
  }

  const value: AuthContextValue = {
    user,
    isLoading,
    isAuthenticated: user !== null,
    login,
    logout,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)

  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }

  return context
}