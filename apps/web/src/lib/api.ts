export interface HealthResponse {
  data: { status: string; service: string; timestamp: string }
}

const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000/api/v1'

export async function getHealth(): Promise<HealthResponse> {
  const response = await fetch(`${apiBaseUrl}/health`)
  if (!response.ok) throw new Error(`API returned ${response.status}`)
  return (await response.json()) as HealthResponse
}
