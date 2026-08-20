export interface Portfolio {
  id: number
  slug: string
  headline: string | null
  bio: string | null
  email: string | null
  phone: string | null
  location: string | null
  linkedin_url: string | null
  github_url: string | null
  skills: string[] | null
  experience: string[] | null
  education: string[] | null
  projects: string[] | null
  certifications: string[] | null
  achievements: string[] | null
  theme: string
  is_published: boolean
  created_at: string
  updated_at: string
}

export interface PortfolioUpdate {
  headline?: string | null
  bio?: string | null
  email?: string | null
  phone?: string | null
  location?: string | null
  linkedin_url?: string | null
  github_url?: string | null
  skills?: string[] | null
  projects?: string[] | null
  is_published?: boolean
}
