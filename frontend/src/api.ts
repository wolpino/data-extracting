/** Thin fetch helpers for /api/v1. No secrets — Gemini key stays server-side. */

export const apiBaseUrl =
  import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export type Order = {
  id: number
  first_name: string
  last_name: string
  date_of_birth: string
  source_filename: string | null
  created_at: string
  updated_at: string
}

export type OrderInput = {
  first_name: string
  last_name: string
  date_of_birth: string
  source_filename?: string | null
}

export type Activity = {
  id: number
  action: string
  entity_type: string
  entity_id: number | null
  method: string | null
  path: string | null
  detail: string | null
  created_at: string
}

export type ExtractDraft = {
  first_name: string
  last_name: string
  date_of_birth: string
}

async function readError(response: Response): Promise<string> {
  let detail = ''
  try {
    const body = (await response.json()) as { detail?: unknown }
    if (typeof body.detail === 'string') detail = body.detail
    else if (Array.isArray(body.detail)) {
      detail = body.detail
        .map((item) => {
          if (item && typeof item === 'object' && 'msg' in item) {
            return String((item as { msg: string }).msg)
          }
          return JSON.stringify(item)
        })
        .join('; ')
    }
  } catch {
    /* ignore non-JSON */
  }

  // Map common extract/API failures to clearer copy (status is the signal).
  if (response.status === 422) {
    return (
      detail ||
      'First name, last name, and date of birth were not found in this PDF. All three fields are required and must appear in the document.'
    )
  }
  if (response.status === 415) {
    return detail || 'Only PDF uploads are supported.'
  }
  if (response.status === 413) {
    return detail || 'File is too large.'
  }
  if (response.status === 429) {
    return detail || 'Rate limited or Gemini quota exhausted — try again later.'
  }
  if (response.status === 502) {
    return detail || 'Extraction failed upstream (Gemini). Try again or check the PDF.'
  }
  if (response.status === 503) {
    return detail || 'Extract service unavailable (is GEMINI_API_KEY set?).'
  }
  return detail || `Request failed (${response.status})`
}

export async function listOrders(): Promise<Order[]> {
  const response = await fetch(`${apiBaseUrl}/api/v1/orders`)
  if (!response.ok) throw new Error(await readError(response))
  return (await response.json()) as Order[]
}

export async function createOrder(input: OrderInput): Promise<Order> {
  const response = await fetch(`${apiBaseUrl}/api/v1/orders`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) throw new Error(await readError(response))
  return (await response.json()) as Order
}

export async function updateOrder(
  id: number,
  input: OrderInput,
): Promise<Order> {
  const response = await fetch(`${apiBaseUrl}/api/v1/orders/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) throw new Error(await readError(response))
  return (await response.json()) as Order
}

export async function deleteOrder(id: number): Promise<void> {
  const response = await fetch(`${apiBaseUrl}/api/v1/orders/${id}`, {
    method: 'DELETE',
  })
  if (!response.ok) throw new Error(await readError(response))
}

/** Upload PDF for draft fields — does not persist an Order. */
export async function extractDocument(file: File): Promise<ExtractDraft> {
  const body = new FormData()
  body.append('file', file)
  const response = await fetch(`${apiBaseUrl}/api/v1/extract`, {
    method: 'POST',
    body,
  })
  if (!response.ok) throw new Error(await readError(response))
  return (await response.json()) as ExtractDraft
}

/** Persist a human-reviewed draft as an Order. */
export async function confirmOrder(input: OrderInput): Promise<Order> {
  const response = await fetch(`${apiBaseUrl}/api/v1/orders/confirm`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(input),
  })
  if (!response.ok) throw new Error(await readError(response))
  return (await response.json()) as Order
}

export async function listActivity(limit = 40): Promise<Activity[]> {
  const response = await fetch(
    `${apiBaseUrl}/api/v1/activity?limit=${limit}`,
  )
  if (!response.ok) throw new Error(await readError(response))
  return (await response.json()) as Activity[]
}
