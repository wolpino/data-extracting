import { useCallback, useEffect, useId, useRef, useState, type FormEvent } from 'react'
import './App.css'
import {
  apiBaseUrl,
  confirmOrder,
  createOrder,
  deleteOrder,
  extractDocument,
  listActivity,
  listOrders,
  type Activity,
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

/** Form origin — draft means extract result not yet confirmed to an Order. */
type FormMode = 'manual' | 'draft' | 'edit'

// Pending mutation — API is called only after explicit Confirm (SPEC).
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

function pendingLabel(pending: Pending): string {
  if (pending.kind === 'create') {
    return `Create order for ${pending.input.first_name} ${pending.input.last_name}?`
  }
  if (pending.kind === 'update') {
    return `Save changes to order #${pending.id}?`
  }
  if (pending.kind === 'confirmExtract') {
    return `Save extracted draft as an Order for ${pending.input.first_name} ${pending.input.last_name}?`
  }
  return `Delete order #${pending.order.id} (${pending.order.first_name} ${pending.order.last_name})?`
}

function App() {
  const [orders, setOrders] = useState<Order[]>([])
  const [activity, setActivity] = useState<Activity[]>([])
  const [form, setForm] = useState<FormState>(emptyForm)
  const [formMode, setFormMode] = useState<FormMode>('manual')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [pending, setPending] = useState<Pending | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [extracting, setExtracting] = useState(false)
  const confirmTitleId = useId()
  const confirmButtonRef = useRef<HTMLButtonElement>(null)

  const refresh = useCallback(async () => {
    const [orderRows, activityRows] = await Promise.all([
      listOrders(),
      listActivity(),
    ])
    setOrders(orderRows)
    setActivity(activityRows)
  }, [])

  useEffect(() => {
    void refresh().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Failed to load orders')
    })
  }, [refresh])

  // Focus primary Confirm when the dialog opens (keyboard / SR friendly).
  useEffect(() => {
    if (pending) confirmButtonRef.current?.focus()
  }, [pending])

  function resetForm() {
    setEditingId(null)
    setFormMode('manual')
    setForm(emptyForm)
    setPending(null)
  }

  function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    const input = toInput(form)
    if (!input.first_name || !input.last_name || !input.date_of_birth) {
      setError('First name, last name, and date of birth are required.')
      return
    }
    // Do not call API yet — wait for Confirm.
    if (formMode === 'draft') {
      setPending({ kind: 'confirmExtract', input })
    } else if (editingId === null) {
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
    setFormMode('edit')
    setForm({
      first_name: order.first_name,
      last_name: order.last_name,
      date_of_birth: order.date_of_birth,
      source_filename: order.source_filename ?? '',
    })
    setPending(null)
    setError(null)
  }

  async function onExtractFile(file: File | null) {
    if (!file) return
    setError(null)
    setPending(null)
    setExtracting(true)
    try {
      const draft = await extractDocument(file)
      setEditingId(null)
      setFormMode('draft')
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

  const formTitle =
    formMode === 'draft'
      ? 'Extracted draft'
      : formMode === 'edit'
        ? `Edit order #${editingId}`
        : 'New order (manual)'

  const primarySubmitLabel =
    formMode === 'draft'
      ? 'Confirm save Order…'
      : formMode === 'edit'
        ? 'Review save…'
        : 'Review create…'

  const locked = busy || extracting || pending !== null

  return (
    <main className="app">
      <h1>Orders</h1>
      <p className="muted">
        API: <code>{apiBaseUrl}</code> — confirm before every save/delete.
      </p>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      <section>
        <h2>Extract from PDF</h2>
        <p className="muted">
          Upload returns a <strong>draft only</strong>. Review fields below,
          then confirm to save an Order.
        </p>
        <input
          type="file"
          accept="application/pdf,.pdf"
          disabled={locked}
          onChange={(e) => {
            const file = e.target.files?.[0] ?? null
            void onExtractFile(file)
            e.target.value = ''
          }}
        />
        {extracting && (
          <p className="status" aria-live="polite">
            Extracting with Gemini… this can take a few seconds.
          </p>
        )}
      </section>

      <section>
        <div className="section-head">
          <h2>{formTitle}</h2>
          {formMode === 'draft' && (
            <span className="badge" title="Not persisted until you confirm">
              Draft — not saved
            </span>
          )}
        </div>
        <form className="form" onSubmit={onSubmit}>
          <label>
            First name
            <input
              value={form.first_name}
              onChange={(e) => setForm({ ...form, first_name: e.target.value })}
              required
              disabled={extracting}
            />
          </label>
          <label>
            Last name
            <input
              value={form.last_name}
              onChange={(e) => setForm({ ...form, last_name: e.target.value })}
              required
              disabled={extracting}
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
              disabled={extracting}
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
              disabled={extracting}
            />
          </label>
          <div className="row">
            <button type="submit" disabled={locked}>
              {primarySubmitLabel}
            </button>
            {(formMode === 'edit' || formMode === 'draft') && (
              <button
                type="button"
                className="secondary"
                disabled={busy || extracting}
                onClick={resetForm}
              >
                {formMode === 'draft' ? 'Discard draft' : 'Cancel edit'}
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
                      disabled={locked}
                      onClick={() => startEdit(order)}
                    >
                      Edit
                    </button>
                    <button
                      type="button"
                      className="danger"
                      disabled={locked}
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

      <section>
        <h2>Recent activity</h2>
        <p className="muted">
          Server audit log (metadata only — no PDF contents).
        </p>
        {activity.length === 0 ? (
          <p className="muted">No activity yet.</p>
        ) : (
          <table>
            <thead>
              <tr>
                <th>When</th>
                <th>Action</th>
                <th>Entity</th>
                <th>Detail</th>
              </tr>
            </thead>
            <tbody>
              {activity.map((row) => (
                <tr key={row.id}>
                  <td>{new Date(row.created_at).toLocaleString()}</td>
                  <td>{row.action}</td>
                  <td>
                    {row.entity_type}
                    {row.entity_id != null ? ` #${row.entity_id}` : ''}
                  </td>
                  <td>{row.detail ?? '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </section>

      {pending && (
        <div
          className="modal-backdrop"
          role="presentation"
          onClick={() => {
            if (!busy) setPending(null)
          }}
        >
          <div
            className="modal"
            role="alertdialog"
            aria-modal="true"
            aria-labelledby={confirmTitleId}
            onClick={(e) => e.stopPropagation()}
          >
            <h3 id={confirmTitleId}>Confirm</h3>
            <p>{pendingLabel(pending)}</p>
            <p className="muted">
              Nothing is written until you confirm (confirm-before-save).
            </p>
            <div className="row">
              <button
                ref={confirmButtonRef}
                type="button"
                disabled={busy}
                onClick={() => void confirmPending()}
              >
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
        </div>
      )}
    </main>
  )
}

export default App
