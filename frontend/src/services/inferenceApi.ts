export type Prediction = {
  label: string
  confidence: number
  low_confidence: boolean
  model_version: string
  architecture: string
  scope: string
}

const API_BASE_URL = import.meta.env.VITE_TSL_API_URL ?? 'http://127.0.0.1:8000'

export async function predictFrame(frame: Blob, signal: AbortSignal): Promise<Prediction> {
  const formData = new FormData()
  formData.append('image', frame, 'camera-frame.jpg')

  const response = await fetch(`${API_BASE_URL}/predict`, {
    method: 'POST',
    body: formData,
    signal,
  })

  if (!response.ok) {
    const payload = await response.json().catch(() => null) as { detail?: string } | null
    throw new Error(payload?.detail ?? `Recognition request failed (${response.status}).`)
  }

  return response.json() as Promise<Prediction>
}
