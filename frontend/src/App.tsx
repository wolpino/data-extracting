import { useCallback, useEffect, useState, type FormEvent } from 'react'
import './App.css'
import {
  apiBaseUrl,
  confirmOrder,
  createOrder,
  deleteOrder,
  extractDocument,
  getApiKey,
  listActivity,
  listOrders,
  setApiKey,
  type Activity,
  type Order,
  type OrderInput,
  updateOrder,
} from './api'
import { formatActivitySummary, formatActivityWhen } from './activityFormat'

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

const ACTIVITY_PAGE = 15

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
  const [activity, setActivity] = useState<Activity[]>([])
  const [activityLimit, setActivityLimit] = useState(ACTIVITY_PAGE)
  const [activityTotalHint, setActivityTotalHint] = useState(0)
  const [form, setForm] = useState<FormState>(emptyForm)
  const [formMode, setFormMode] = useState<FormMode>('manual')
  const [editingId, setEditingId] = useState<number | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)
  const [extracting, setExtracting] = useState(false)
  // Inline delete confirm — Confirm / Cancel buttons on the row (not window.confirm).
  const [deleteCandidate, setDeleteCandidate] = useState<Order | null>(null)
  // Demo shared key (session only). Required when server API_KEY is set.
  const [apiKeyInput, setApiKeyInput] = useState(() => getApiKey())

  const refreshOrders = useCallback(async () => {
    setOrders(await listOrders())
  }, [])

  const refreshActivity = useCallback(async (limit: number) => {
    // Fetch one extra to know if "load more" should show.
    const rows = await listActivity(limit + 1)
    setActivityTotalHint(rows.length)
    setActivity(rows.slice(0, limit))
  }, [])

  const refresh = useCallback(async () => {
    await Promise.all([refreshOrders(), refreshActivity(activityLimit)])
  }, [refreshOrders, refreshActivity, activityLimit])

  useEffect(() => {
    void refresh().catch((err: unknown) => {
      setError(err instanceof Error ? err.message : 'Failed to load')
    })
  }, [refresh])

  function resetForm() {
    setEditingId(null)
    setFormMode('manual')
    setForm(emptyForm)
  }

  async function onSubmit(event: FormEvent) {
    event.preventDefault()
    setError(null)
    const input = toInput(form)
    if (!input.first_name || !input.last_name || !input.date_of_birth) {
      setError('First name, last name, and date of birth are required.')
      return
    }
    setBusy(true)
    try {
      // Button label is the human confirm — no second modal (extract / create / save).
      if (formMode === 'draft') {
        await confirmOrder(input)
      } else if (editingId === null) {
        await createOrder(input)
      } else {
        await updateOrder(editingId, input)
      }
      await refresh()
      resetForm()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Request failed')
    } finally {
      setBusy(false)
    }
  }

  async function confirmDelete() {
    if (!deleteCandidate) return
    const order = deleteCandidate
    setError(null)
    setBusy(true)
    try {
      await deleteOrder(order.id)
      setDeleteCandidate(null)
      await refresh()
      if (editingId === order.id) resetForm()
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Delete failed')
    } finally {
      setBusy(false)
    }
  }

  function startEdit(order: Order) {
    setDeleteCandidate(null)
    setEditingId(order.id)
    setFormMode('edit')
    setForm({
      first_name: order.first_name,
      last_name: order.last_name,
      date_of_birth: order.date_of_birth,
      source_filename: order.source_filename ?? '',
    })
    setError(null)
  }

  async function onExtractFile(file: File | null) {
    if (!file) return
    setError(null)
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
      // Incomplete / failed extract must not leave a half-filled draft.
      resetForm()
      setError(err instanceof Error ? err.message : 'Extract failed')
    } finally {
      setExtracting(false)
    }
  }

  async function loadMoreActivity() {
    const next = activityLimit + ACTIVITY_PAGE
    setActivityLimit(next)
    setBusy(true)
    try {
      await refreshActivity(next)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load activity')
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
      ? 'Confirm & save Order'
      : formMode === 'edit'
        ? 'Save changes'
        : 'Create Order'

  const locked = busy || extracting
  const canLoadMoreActivity = activityTotalHint > activityLimit

  return (
    <main className="app">
      <h1>The Extractor</h1>
      <p className="muted">
        API: <code>{apiBaseUrl}</code> — review extracted fields, then{' '}
        <strong>Confirm &amp; save</strong> (or create/save manually).
      </p>

      <label className="api-key-field">
        Demo API key
        <input
          type="password"
          autoComplete="off"
          placeholder="Paste from README when API_KEY is set on the server"
          value={apiKeyInput}
          onChange={(e) => {
            const value = e.target.value
            setApiKeyInput(value)
            setApiKey(value)
          }}
        />
      </label>
      <p className="muted api-key-hint">
        Stored in sessionStorage only (not baked into the Vite build). Leave
        blank for local APIs with no <code>API_KEY</code>.
      </p>

      {error && (
        <p className="error" role="alert">
          {error}
        </p>
      )}

      <section>
        <h2>Extract from PDF</h2>
        <p className="muted">
          Upload returns a draft only when first name, last name, and DOB are
          all found. Incomplete PDFs show an error and do not fill the form.
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

      <div className="workspace">
        <section className="workspace-main">
          <div className="section-head">
            <h2>{formTitle}</h2>
            {formMode === 'draft' && (
              <span className="badge" title="Not persisted until you confirm & save">
                Draft — not saved
              </span>
            )}
          </div>
          <form className="form" onSubmit={(e) => void onSubmit(e)}>
            <label>
              First name
              <input
                value={form.first_name}
                onChange={(e) =>
                  setForm({ ...form, first_name: e.target.value })
                }
                required
                disabled={extracting}
              />
            </label>
            <label>
              Last name
              <input
                value={form.last_name}
                onChange={(e) =>
                  setForm({ ...form, last_name: e.target.value })
                }
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

        <aside className="activity-panel" aria-label="Recent activity">
          <h2>Activity</h2>
          <p className="muted activity-help">
            What happened recently (no file contents).
          </p>
          <div className="activity-scroll">
            {activity.length === 0 ? (
              <p className="muted">No activity yet.</p>
            ) : (
              <ul className="activity-list">
                {activity.map((row) => {
                  const when = formatActivityWhen(row.created_at)
                  return (
                    <li key={row.id}>
                      <div className="activity-when">
                        <span className="activity-relative">{when.relative}</span>
                        <span className="activity-absolute">{when.absolute}</span>
                      </div>
                      <div className="activity-summary">
                        {formatActivitySummary(row)}
                      </div>
                    </li>
                  )
                })}
              </ul>
            )}
          </div>
          {canLoadMoreActivity && (
            <button
              type="button"
              className="secondary activity-more"
              disabled={busy}
              onClick={() => void loadMoreActivity()}
            >
              Load more
            </button>
          )}
        </aside>
      </div>

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
                    {deleteCandidate?.id === order.id ? (
                      <>
                        <button
                          type="button"
                          className="danger"
                          disabled={busy}
                          onClick={() => void confirmDelete()}
                        >
                          Confirm delete
                        </button>
                        <button
                          type="button"
                          className="secondary"
                          disabled={busy}
                          onClick={() => setDeleteCandidate(null)}
                        >
                          Cancel
                        </button>
                      </>
                    ) : (
                      <>
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
                          onClick={() => {
                            setError(null)
                            setDeleteCandidate(order)
                          }}
                        >
                          Delete
                        </button>
                      </>
                    )}
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
