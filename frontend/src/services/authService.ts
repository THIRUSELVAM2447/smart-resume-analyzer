import { api } from './api'
import { setAccessToken, clearAccessToken } from '../utils/authToken'
import type {
  User,
  LoginRequest,
  RegisterRequest,
  AuthResponse,
} from '../types/auth'

export const authService = {
  register: (userData: RegisterRequest): Promise<User> => {
    return api.post<User>('/api/auth/register', userData)
  },

  login: async (credentials: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>(
      '/api/auth/login',
      credentials
    )

    setAccessToken(response.access_token)

    return response
  },

  getCurrentUser: (): Promise<User> => {
    return api.get<User>('/api/auth/me')
  },

  logout: (): void => {
    clearAccessToken()
  },
}