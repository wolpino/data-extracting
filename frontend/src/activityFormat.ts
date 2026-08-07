/** Turn raw activity rows into short human-readable lines for the aside panel. */

import type { Activity } from './api'

const ACTION_LABELS: Record<string, string> = {
  confirm: 'Confirmed & saved',
  create: 'Created',
  update: 'Updated',
  delete: 'Deleted',
  get: 'Opened',
  list: 'Viewed order list',
  extract: 'Extracted PDF',
}

function entityPhrase(row: Activity): string {
  if (row.entity_type === 'order' && row.entity_id != null) {
    return `order #${row.entity_id}`
  }
  if (row.entity_type === 'document') {
    return 'a document'
  }
  if (row.entity_type === 'order') {
    return 'orders'
  }
  return row.entity_type
}

function parseDetail(detail: string | null): string | null {
  if (!detail) return null
  // extract logs: filename=foo.pdf; bytes=1234
  const fileMatch = detail.match(/filename=([^;]+)/i)
  if (fileMatch) {
    const name = fileMatch[1].trim()
    if (name && name !== 'unknown') return `File: ${name}`
  }
  const countMatch = detail.match(/count=(\d+)/i)
  if (countMatch) return `${countMatch[1]} order(s)`
  // put/patch crumbs — show as-is if short
  if (detail.length <= 80) return detail
  return null
}

export function formatActivitySummary(row: Activity): string {
  const verb = ACTION_LABELS[row.action] ?? row.action
  if (row.action === 'list') {
    const extra = parseDetail(row.detail)
    return extra ? `${verb} (${extra})` : verb
  }
  if (row.action === 'extract') {
    const extra = parseDetail(row.detail)
    return extra ? `${verb} — ${extra}` : verb
  }
  return `${verb} ${entityPhrase(row)}`
}

export function parseActivityDate(iso: string): Date {
  // SQLite/SQLAlchemy often emit naive UTC timestamps without "Z"; JS would
  // treat those as local and skew relative times (everything looks "Just now").
  const trimmed = iso.trim()
  if (/[zZ]$|[+-]\d{2}:\d{2}$/.test(trimmed)) {
    return new Date(trimmed)
  }
  if (/^\d{4}-\d{2}-\d{2}T/.test(trimmed)) {
    return new Date(`${trimmed}Z`)
  }
  return new Date(trimmed)
}

export function formatActivityWhen(iso: string): {
  relative: string
  absolute: string
} {
  const when = parseActivityDate(iso)
  const absolute = when.toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
    second: '2-digit',
  })
  if (Number.isNaN(when.getTime())) {
    return { relative: iso, absolute: iso }
  }
  const seconds = Math.max(0, Math.round((Date.now() - when.getTime()) / 1000))
  let relative: string
  if (seconds < 45) relative = 'Just now'
  else if (seconds < 3600) {
    const m = Math.max(1, Math.round(seconds / 60))
    relative = `${m} min ago`
  } else if (seconds < 86400) {
    const h = Math.max(1, Math.round(seconds / 3600))
    relative = `${h} hr ago`
  } else {
    relative = when.toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
    })
  }
  return { relative, absolute }
}
