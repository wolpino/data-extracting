import { useCallback, useEffect, useState, type FormEvent } from 'react'
import './App.css'
import {
  apiBaseUrl,
  confirmOrder,
  createOrder,
  deleteOrder,
  extractDocument,
  listOrders,
  type Order,
  type OrderInput,
  updateOrder,
} from './api'

type FormState = {
  first_name: string
  last_name: string
  date_of_birth: string
  source_filename: string
}

const emptyForm: FormState = {
  first_name: '',
  last_name: '',
  date_of_birth: '',
  source_filename: '',
}

// Pending mutation — API is called only after explicit Confirm (SPEC).
// UX debt: banner at top is clunky — replace with near-action modal later.
type Pending =
  | { kind: 'create'; input: OrderInput }
  | { kind: 'update'; id: number; input: OrderInput }
  | { kind: 'delete'; order: Order }
  | { kind: 'confirmExtract'; input: OrderInput }

function toInput(form: FormState): OrderInput {
  const filename = form.source_filename.trim()
  return {
    first_name: form.first_name.trim(),
    last_name: form.last_name.trim(),
    date_of_birth: form.date_of_birth,
    source_filename: filename.length > 0 ? filename : null,
  }
}

function App() {
  const [orders, setOrders] = useState<Order[]>([])
  const [form, setForm] = useState<FormState>(emptyForm)
  const [editingId, setEditingId] = useState<number | null>(null)
  const [pending, setPending] = useState<Pending | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [extracting, setExtracting] = useState(false)

  const refresh = useCallback(async () => {
    const rows = await listOrders()
    setOrders(rows)
  }, [])

  useEffect(() => {
    void refresh().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Failed to load orders')
    })
  }, [refresh])

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    const input = toInput(form)
    if (!input.first_name || !input.last_name || !input.date_of_birth) {
      setError('First name, last name, and date of birth are required.')
      return
    }
    // Do not call API yet — wait for Confirm.
    if (editingId === null) {
      setPending({ kind: 'create', input })
    } else {
      setPending({ kind: 'update', id: editingId, input })
    }
  }

  function requestDelete(order: Order) {
    setError(null)
    setPending({ kind: 'delete', order })
  }

  function startEdit(order: Order) {
    setEditingId(order.id)
    setForm({
      first_name: order.first_name,
      last_name: order.last_name,
      date_of_birth: order.date_of_birth,
      source_filename: order.source_filename ?? '',
    })
    setPending(null)
    setError(null)
  }

  function resetForm() {
    setEditingId(null)
    setForm(emptyForm)
    setPending(null)
  }

  async function onExtractFile(file: File | null) {
    if (!file) return
    setError(null)
    setPending(null)
    setExtracting(true)
    try {
      const draft = await extractDocument(file)
      setEditingId(null)
      setForm({
        first_name: draft.first_name,
        last_name: draft.last_name,
        date_of_birth: draft.date_of_birth,
        source_filename: file.name,
      })
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Extract failed')
    } finally {
      setExtracting(false)
    }
  }

  function reviewExtractConfirm() {
    setError(null)
    const input = toInput(form)
    if (!input.first_name || !input.last_name || !input.date_of_birth) {
      setError('First name, last name, and date of birth are required.')
      return
    }
    setPending({ kind: 'confirmExtract', input })
  }

  async function confirmPending() {
    if (!pending) return
    setBusy(true)
    setError(null)
    try {
      if (pending.kind === 'create') {
        await createOrder(pending.input)
      } else if (pending.kind === 'update') {
        await updateOrder(pending.id, pending.input)
      } else if (pending.kind === 'confirmExtract') {
        await confirmOrder(pending.input)
      } else {
        await deleteOrder(pending.order.id)
      }
      await refresh()
      resetForm()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Request failed')
      setPending(null)
    } finally {
      setBusy(false)
    }
  }

  const pendingLabel = (() => {
    if (!pending) return ''
    if (pending.kind === 'create') {
      return `Create order for ${pending.input.first_name} ${pending.input.last_name}?`
    }
    if (pending.kind === 'update') {
      return `Save changes to order #${pending.id}?`
    }
    if (pending.kind === 'confirmExtract') {
      return `Confirm extracted order for ${pending.input.first_name} ${pending.input.last_name}?`
    }
    return `Delete order #${pending.order.id} (${pending.order.first_name} ${pending.order.last_name})?`
  })()

  return (
    <main className="app">
      <h1>Orders</h1>
      <p className="muted">
        API: <code>{apiBaseUrl}</code> — confirm before every save/delete.
      </p>

      {error && <p className="error">{error}</p>}

      {pending && (
        <div className="confirm" role="alertdialog" aria-label="Confirm action">
          <p>{pendingLabel}</p>
          <p className="muted">
            Temporary confirm UI — will move near the action later.
          </p>
          <div className="row">
            <button type="button" disabled={busy} onClick={() => void confirmPending()}>
              Confirm
            </button>
            <button
              type="button"
              className="secondary"
              disabled={busy}
              onClick={() => setPending(null)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      <section>
        <h2>Extract from PDF</h2>
        <p className="muted">
          Upload returns a draft only. Review fields, then Confirm to save an
          Order.
        </p>
        <input
          type="file"
          accept="application/pdf,.pdf"
          disabled={busy || extracting || pending !== null}
          onChange={(e) => {
            const file = e.target.files?.[0] ?? null
            void onExtractFile(file)
            e.target.value = ''
          }}
        />
        {extracting && <p className="muted">Extracting…</p>}
        <div className="row" style={{ marginTop: '0.75rem' }}>
          <button
            type="button"
            disabled={busy || extracting || pending !== null}
            onClick={reviewExtractConfirm}
          >
            Review extract save…
          </button>
        </div>
      </section>

      <section>
        <h2>{editingId === null ? 'New order' : `Edit order #${editingId}`}</h2>
        <form className="form" onSubmit={onSubmit}>
          <label>
            First name
            <input
              value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })}
              required
            />
          </label>
          <label>
            Last name
            <input
              value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })}
              required
            />
          </label>
          <label>
            Date of birth
            <input
              type="date"
              value={form.date_of_birth}
              onChange={(e) =>
                setForm({ ...form, date_of_birth: e.target.value })
              }
              required
            />
          </label>
          <label>
            Source filename (optional)
            <input
              value={form.source_filename}
              onChange={(e) =>
                setForm({ ...form, source_filename: e.target.value })
              }
              placeholder="chart.pdf"
            />
          </label>
          <div className="row">
            <button type="submit" disabled={busy || pending !== null}>
              {editingId === null ? 'Review create…' : 'Review save…'}
            </button>
            {editingId !== null && (
              <button
                type="button"
                className="secondary"
                disabled={busy}
                onClick={resetForm}
              >
                Cancel edit
              </button>
            )}
          </div>
        </form>
      </section>

      <section>
        <h2>All orders</h2>
        {orders.length === 0 ? (
          <p className="muted">No orders yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>DOB</th>
                <th>File</th>
                <th />
              </tr>
            </thead>
            <tbody>
              {orders.map((order) => (
                <tr key={order.id}>
                  <td>{order.id}</td>
                  <td>
                    {order.first_name} {order.last_name}
                  </td>
                  <td>{order.date_of_birth}</td>
                  <td>{order.source_filename ?? '—'}</td>
                  <td className="row">
                    <button
                      type="button"
                      className="secondary"
                      disabled={busy || pending !== null}
                      onClick={() => startEdit(order)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="danger"
                      disabled={busy || pending !== null}
                      onClick={() => requestDelete(order)}
                    >
                      Delete…
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>
    </main>
  )
}

export default App
