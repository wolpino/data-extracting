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

export function formatActivityWhen(iso: string): { label: string; title: string } {
  const when = new Date(iso)
  const title = when.toLocaleString()
  const seconds = Math.round((Date.now() - when.getTime()) / 1000)
  if (Number.isNaN(seconds)) return { label: title, title }
  if (seconds < 45) return { label: 'Just now', title }
  if (seconds < 3600) {
    const m = Math.max(1, Math.round(seconds / 60))
    return { label: `${m} min ago`, title }
  }
  if (seconds < 86400) {
    const h = Math.max(1, Math.round(seconds / 3600))
    return { label: `${h} hr ago`, title }
  }
  return {
    label: when.toLocaleString(undefined, {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    }),
    title,
  }
}
