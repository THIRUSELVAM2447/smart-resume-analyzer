export interface Job {
  id: number
  title: string | null
  company_name: string | null
  source_url: string | null
  description: string
  source_type: string
  created_at: string
  updated_at: string
}

export interface JobCreate {
  title?: string
  company_name?: string
  source_url?: string
  description: string
  source_type: string
}
