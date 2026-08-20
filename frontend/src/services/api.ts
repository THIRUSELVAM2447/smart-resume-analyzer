// Reusable, framework-free API client built on the browser's fetch().
// Future files (authService.ts, resumeService.ts) will call these
// methods instead of using fetch() directly.

import { getAccessToken } from '../utils/authToken'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

if (!API_BASE_URL) {
  throw new Error(
    'VITE_API_BASE_URL is missing. Create a file named .env.local inside ' +
      'the frontend folder with this line:\n' +
      'VITE_API_BASE_URL=http://127.0.0.1:8000'
  )
}

// Shape of the error thrown when the backend responds with a non-2xx status.
export interface ApiError {
  status: number
  statusText: string
  message: string
}

type HttpMethod = 'GET' | 'POST' | 'PATCH' | 'DELETE'

interface RequestOptions {
  body?: unknown
  headers?: Record<string, string>
}

function getBackendMessage(body: unknown, fallback: string): string {
  if (!body || typeof body !== 'object' || !('detail' in body)) {
    return fallback
  }

  const detail = (body as { detail: unknown }).detail

  if (typeof detail === 'string') {
    return detail
  }

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) =>
        item && typeof item === 'object' && 'msg' in item
          ? String((item as { msg: unknown }).msg)
          : null
      )
      .filter((message): message is string => Boolean(message))

    return messages.join(' ') || fallback
  }

  return fallback
}

async function request<TResponse>(
  method: HttpMethod,
  path: string,
  options: RequestOptions = {}
): Promise<TResponse> {
  const { body, headers = {} } = options

  const finalHeaders: Record<string, string> = { ...headers }
  let requestBody: BodyInit | undefined

  if (body !== undefined) {
    if (body instanceof FormData) {
      requestBody = body
    } else {
      finalHeaders['Content-Type'] = 'application/json'
      requestBody = JSON.stringify(body)
    }
  }

  // Automatically attach the stored JWT, unless the caller already
  // supplied their own Authorization header (checked case-insensitively,
  // since HTTP header names are case-insensitive even though JS object
  // keys are not).
  const hasAuthorizationHeader = Object.keys(finalHeaders).some(
    (key) => key.toLowerCase() === 'authorization'
  )

  if (!hasAuthorizationHeader) {
    const token = getAccessToken()
    if (token) {
      finalHeaders['Authorization'] = `Bearer ${token}`
    }
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    method,
    headers: finalHeaders,
    body: requestBody,
  })

  // Read the response as text first, since some responses (e.g. DELETE)
  // may come back with an empty body, which JSON.parse() cannot handle.
  const rawText = await response.text()
  let parsedBody: unknown = undefined

  if (rawText.length > 0) {
    try {
      parsedBody = JSON.parse(rawText)
    } catch {
      // Backend didn't return JSON — keep the raw text instead of crashing.
      parsedBody = rawText
    }
  }

  if (!response.ok) {
    const apiError: ApiError = {
      status: response.status,
      statusText: response.statusText,
      message: getBackendMessage(parsedBody, response.statusText),
    }

    throw apiError
  }

  return parsedBody as TResponse
}

export const api = {
  get: <TResponse>(path: string, options?: RequestOptions) =>
    request<TResponse>('GET', path, options),

  post: <TResponse>(path: string, body?: unknown, options?: RequestOptions) =>
    request<TResponse>('POST', path, { ...options, body }),

  patch: <TResponse>(path: string, body?: unknown, options?: RequestOptions) =>
    request<TResponse>('PATCH', path, { ...options, body }),

  delete: <TResponse>(path: string, options?: RequestOptions) =>
    request<TResponse>('DELETE', path, options),
}
