// Types for resume/domain data, matching the backend's ResumeResponse,
// ResumeDetailResponse, and ResumeVersionResponse schemas.

// Represents the backend's JSONValue: arbitrary JSON that can recursively
// contain objects, arrays, strings, numbers, booleans, or null. Used for
// resume-version fields whose internal application-specific structure
// (e.g. what a "skills" entry looks like) is not yet confirmed.
export type JSONValue =
  | { [key: string]: JSONValue }
  | JSONValue[]
  | string
  | number
  | boolean
  | null

// Matches ResumeResponse. Deliberately excludes user_id and file_path,
// since the backend does not return them.
export interface Resume {
  id: number
  original_filename: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// Matches ResumeVersionResponse.
export interface ResumeVersion {
  id: number
  resume_id: number
  version_number: number
  raw_text: string
  full_name: string | null
  email: string | null
  phone: string | null
  location: string | null
  linkedin_url: string | null
  github_url: string | null
  summary: string | null
  skills: JSONValue | null
  experience: JSONValue | null
  education: JSONValue | null
  projects: JSONValue | null
  certifications: JSONValue | null
  achievements: JSONValue | null
  created_at: string
}

// Matches ResumeDetailResponse: a Resume plus its list of versions.
export interface ResumeDetail extends Resume {
  versions: ResumeVersion[]
}