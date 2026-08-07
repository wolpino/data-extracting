/** Thin fetch helpers for /api/v1/orders. No secrets — API key stays server-side. */

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

async function readError(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: unknown }
    if (typeof body.detail === 'string') return body.detail
    if (Array.isArray(body.detail)) {
      return body.detail
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
  return `Request failed (${response.status})`
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
