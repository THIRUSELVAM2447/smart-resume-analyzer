// Mirrors the error shape thrown by src/services/api.ts when the backend
// responds with a non-2xx status. Keep this in sync with api.ts if that
// file's error shape ever changes.
export interface ApiError {
  status: number
  statusText: string
  message: string
}